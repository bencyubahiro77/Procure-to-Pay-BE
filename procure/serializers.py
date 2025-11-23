from django.http import QueryDict
from rest_framework import serializers
from procure.models import PurchaseRequest, RequestItem, Approval, PurchaseOrder, ReceiptValidation
import json

class RequestItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = RequestItem
        fields = ['id', 'name', 'qty', 'unit_price', 'total_price']
        read_only_fields = ['id', 'total_price']

    def get_total_price(self, obj):
        return str(obj.total_price)


class RequestItemInputSerializer(serializers.Serializer):
    """Serializer for item input - used in write operations"""
    name = serializers.CharField(max_length=255)
    qty = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2)


class ApprovalSerializer(serializers.ModelSerializer):
    approver = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Approval
        fields = ['id', 'request', 'approver', 'level', 'approved', 'comment', 'created_at']
        read_only_fields = ['approver', 'level', 'created_at']


from drf_spectacular.utils import extend_schema_field

class PurchaseRequestSerializer(serializers.ModelSerializer):
    items = RequestItemInputSerializer(many=True, required=False, write_only=True)
    items_display = RequestItemSerializer(source='items', many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    last_approved_by = serializers.StringRelatedField(read_only=True)
    approvals = ApprovalSerializer(many=True, read_only=True)
    proforma = serializers.FileField(required=False, allow_null=True)
    purchase_order = serializers.SerializerMethodField()
    receipt = serializers.SerializerMethodField()
    receipt_validation = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseRequest
        fields = ['id', 'title', 'description', 'vendor', 'amount', 'status', 'created_by', 'last_approved_by',
                  'created_at', 'proforma', 'purchase_order', 'receipt', 'receipt_validation', 'items', 'items_display', 'approvals']
        read_only_fields = ['status', 'created_by', 'created_at', 'last_approved_by']

    
    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_purchase_order(self, obj):
        """Return full Cloudinary URL for the PO file"""
        if hasattr(obj, 'po_obj') and obj.po_obj and obj.po_obj.file:
            return obj.po_obj.file.url
        return None
    
    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_receipt(self, obj):
        """Return full Cloudinary URL for the receipt file"""
        if obj.receipt:
            return obj.receipt.url
        return None
    
    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_receipt_validation(self, obj):
        """Return receipt validation status and discrepancies"""
        if hasattr(obj, 'receipt_validation') and obj.receipt_validation:
            rv = obj.receipt_validation
            return {
                'is_valid': rv.is_valid,
                'validated_at': rv.validated_at,
                'discrepancies': rv.discrepancies or []
            }
        return None

    def to_internal_value(self, data):
        """Handle multipart/form-data conversion of items field"""
        if isinstance(data, QueryDict):
            data = data.dict()

        # Parse items if it's a JSON string (from multipart/form-data)
        items = data.get('items')
        
        if items and isinstance(items, str):
            try:
                parsed = json.loads(items)
                
                # Ensure it's a list
                if isinstance(parsed, dict):
                    items = [parsed]
                elif isinstance(parsed, list):
                    items = parsed
                else:
                    items = []
                    
                data['items'] = items
            except json.JSONDecodeError:
                pass  # Let validation handle the error

        return super().to_internal_value(data)

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        user = self.context['request'].user
        
        pr = PurchaseRequest.objects.create(created_by=user, **validated_data)

        for item_data in items_data:
            RequestItem.objects.create(
                request=pr,
                name=item_data['name'],
                qty=item_data['qty'],
                unit_price=item_data['unit_price']
            )

        pr.refresh_from_db()
        return pr

    def update(self, instance, validated_data):
        if instance.status != PurchaseRequest.STATUS_PENDING:
            raise serializers.ValidationError('Cannot modify a request that is not pending')
        
        if instance.approvals.exists():
            raise serializers.ValidationError('Cannot modify a request that has already been approved by Level 1')
        
        items_data = validated_data.pop('items', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                RequestItem.objects.create(
                    request=instance,
                    name=item_data['name'],
                    qty=item_data['qty'],
                    unit_price=item_data['unit_price']
                )
        
        instance.refresh_from_db()
        return instance


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'request', 'generated_at', 'generated_by', 'content', 'file']
    def create(self, validated_data):
        user = self.context['request'].user
        po = PurchaseOrder.objects.create(generated_by=user, **validated_data)
        po.refresh_from_db()
        return po
    

