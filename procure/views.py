from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect as django_redirect

from procure.models import PurchaseRequest, Approval
from procure.serializers import PurchaseRequestSerializer, PurchaseOrderSerializer
from procure.document_processing import generate_po_for_request, validate_receipt_against_po_with_text, extract_text_from_pdf

from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers
from accounts.permissions import IsInRoles, IsFinance
import cloudinary


from procure_to_pay.utils import RequestPagination
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync

class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all().prefetch_related("items")
    serializer_class = PurchaseRequestSerializer
    pagination_class = RequestPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # Enable search & filters
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    # Fields searchable using ?search=keyword
    search_fields = [
        'title',
        'description',
        'status',
        'created_by__email',
    ]

    # Fields sortable using ?ordering=-amount or ?ordering=created_at
    ordering_fields = [
        'amount',
        'created_at',
        'status',
    ]

    def get_permissions(self):
        # Configure permissions per action:
        # - create: only staff
        # - approve/reject: only approvers
        # - list/retrieve: staff (own), approvers, admin (view all)
        # - submit-receipt: only staff (we'll also check owner in method)
        if self.action == "create":
            return [IsAuthenticated(), IsInRoles(["staff"])]
        if self.action in ("approve", "reject"):
            return [IsAuthenticated(), IsInRoles(["approver_l1", "approver_l2"])]
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated(), IsInRoles(["staff", "approver_l1", "approver_l2", "finance" ,"admin"])]
        if self.action == "submit_receipt":
            return [IsAuthenticated(), IsInRoles(["staff"])]
        # default: require authentication
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, "profile"):
            return self.queryset.none()

        role = user.profile.role

        if role == "staff":
            # Staff see only their own requests
            return self.queryset.filter(created_by=user).order_by('-created_at')
        
        elif role == "approver_l1":
            # Approver 1 sees all requests
            return self.queryset.all().order_by('-created_at')
        
        elif role == "approver_l2":
            # Approver 2 only sees requests approved by Approver 1
            return self.queryset.filter(approvals__level=1, approvals__approved=True).order_by('-created_at')
        
        elif role == "finance":
            # Finance only sees requests approved by Approver 2 (status is APPROVED)
            return self.queryset.filter(status="APPROVED").order_by('-created_at')
        
        elif role == "admin":
            # Admin sees all requests
            return self.queryset.all().order_by('-created_at')

        # Everything else: nothing
        return self.queryset.none()

    @extend_schema(
        description="""
        List purchase requests with role-based filtering:
        - **Staff**: Sees only their own requests.
        - **Approver L1**: Sees ALL requests.
        - **Approver L2**: Sees only requests approved by L1.
        - **Finance**: Sees only fully approved requests (approved by L2).
        - **Admin**: Sees all requests.
        """
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=PurchaseRequestSerializer,
        responses={201: PurchaseRequestSerializer},
        description="Create a new purchase request"
    )
    def perform_create(self, serializer):
        # only staff can reach here due to get_permissions
        serializer.save()

    @extend_schema(
        request=inline_serializer(
            name="ApprovalRequest",
            fields={
                "comment": drf_serializers.CharField(
                    required=False,
                    allow_blank=True,
                    help_text="Optional approval comment"
                )
            },
        ),
        responses={
            200: inline_serializer(
                name="ApprovalResponse",
                fields={
                    "detail": drf_serializers.CharField(),
                    "po": PurchaseOrderSerializer(required=False)
                },
            ),
            400: OpenApiResponse(description="Bad Request"),
            403: OpenApiResponse(description="Forbidden"),
        },
        description="Approve a purchase request. L1 approves, L2 finalizes + generates PO."
    )
    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, pk=None):
        user = request.user
        pr = get_object_or_404(PurchaseRequest, pk=pk)

        if pr.status != PurchaseRequest.STATUS_PENDING:
            return Response(
                {"detail": "Request is already finalized."},
                status=status.HTTP_400_BAD_REQUEST
            )

        role = user.profile.role if hasattr(user, "profile") else None

        if role == "approver_l1":
            level = 1
        elif role == "approver_l2":
            level = 2
        else:
            return Response(
                {"detail": "Not authorized to approve."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment = request.data.get("comment", "")

        with transaction.atomic():
            pr = PurchaseRequest.objects.select_for_update().get(pk=pr.pk)

            if Approval.objects.filter(request=pr, approver=user, level=level).exists():
                return Response(
                    {"detail": "You already approved this request."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Approval.objects.create(
                request=pr,
                approver=user,
                approved=True,
                level=level,
                comment=comment,
            )

            if level == 1:
                return Response({"detail": "Level 1 approval recorded."})

            if not pr.approvals.filter(level=1, approved=True).exists():
                return Response(
                    {"detail": "Cannot approve at Level 2 before Level 1 approval."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            pr.status = PurchaseRequest.STATUS_APPROVED
            pr.save()

            po = generate_po_for_request(pr)
            po_data = PurchaseOrderSerializer(po).data

        return Response(
            {"detail": "Purchase request approved.", "po": po_data},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        request=inline_serializer(
            name="RejectionRequest",
            fields={
                "comment": drf_serializers.CharField(required=False, allow_blank=True)
            }
        ),
        description="Reject a purchase request"
    )
    @action(detail=True, methods=["patch"], url_path="reject")
    def reject(self, request, pk=None):
        user = request.user
        pr = get_object_or_404(PurchaseRequest, pk=pk)

        if pr.status != PurchaseRequest.STATUS_PENDING:
            return Response(
                {"detail": "Request already finalized."},
                status=status.HTTP_400_BAD_REQUEST
            )

        role = user.profile.role if hasattr(user, "profile") else None

        if role not in ("approver_l1", "approver_l2"):
            return Response(
                {"detail": "Not authorized to reject."},
                status=status.HTTP_403_FORBIDDEN
            )

        comment = request.data.get("comment", "")

        with transaction.atomic():
            pr = PurchaseRequest.objects.select_for_update().get(pk=pr.pk)

            Approval.objects.create(
                request=pr,
                approver=user,
                approved=False,
                level=1 if role == "approver_l1" else 2,
                comment=comment,
            )

            pr.status = PurchaseRequest.STATUS_REJECTED
            pr.save()

        return Response({"detail": "Purchase request rejected."})

    @extend_schema(
        request=inline_serializer(
            name='ReceiptUploadRequest',
            fields={
                'receipt': drf_serializers.FileField(help_text="Receipt file to upload")
            }
        ),
        responses={
            200: inline_serializer(
                name='ReceiptUploadResponse',
                fields={
                    'detail': drf_serializers.CharField(),
                    'validation': inline_serializer(
                        name='ValidationResult',
                        fields={
                            'ok': drf_serializers.BooleanField(),
                            'discrepancies': drf_serializers.ListField(child=drf_serializers.CharField()),
                            'is_valid': drf_serializers.BooleanField()
                        }
                    )
                }
            ),
            400: OpenApiResponse(description="Bad request")
        },
        description="Upload receipt for an approved purchase request"
    )
    @action(detail=True, methods=["post"], url_path="submit-receipt")
    def submit_receipt(self, request, pk=None):
        pr = get_object_or_404(PurchaseRequest, pk=pk)

        # Only the staff who created the request may submit its receipt
        if request.user != pr.created_by:
            return Response(
                {"detail": "Only the request owner can submit a receipt."},
                status=status.HTTP_403_FORBIDDEN
            )

        if pr.status != PurchaseRequest.STATUS_APPROVED:
            return Response(
                {"detail": "Only approved requests can accept receipts."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if "receipt" not in request.FILES:
            return Response(
                {"detail": "Receipt file is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        receipt_file = request.FILES["receipt"]
        
        # Extract text BEFORE uploading to Cloudinary (in backend memory)
        try:
            receipt_text = extract_text_from_pdf(receipt_file)
            # Reset file pointer after reading so it can be saved
            receipt_file.seek(0)
        except Exception as e:
            return Response(
                {"detail": f"Failed to process receipt: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the file (this uploads to Cloudinary)
        pr.receipt = receipt_file
        pr.save()
        
        # Perform synchronous validation
        try:
            # validate_receipt_against_po_with_text is synchronous, so we call it directly
            validation_result = validate_receipt_against_po_with_text(pr, receipt_text)
            
            return Response(
                {
                    "detail": "Receipt submitted and validated successfully.",
                    "validation": validation_result
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": f"Validation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
