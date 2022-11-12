from rest_framework import serializers
from .models import ReadingDataModel

from pytz import timezone
from datetime import datetime

def make_date_time():
    fmt = "%Y-%m-%d %H:%M:%S"
    KST = datetime.now(timezone('Asia/Seoul'))
    return KST.strftime(fmt)


class ReadingDataEditSerializer(serializers.ModelSerializer):
    
    title= serializers.CharField(max_length=100)
    actual_rsrc_txt =serializers.CharField(max_length=1000000000)    
    
    class Meta:
        model = ReadingDataModel
        fields = ('title', 'actual_rsrc_txt')
        
    def update(self, instance, validated_data):
        validated_data["modified_at"] =make_date_time()
        
        html_content = "<p class='MuiTypography-root MuiTypography-body1' style='font-family: CookieRun-Regular;'>%s</p>" % (validated_data["actual_rsrc_txt"]) 
        validated_data["highlight_html"] =html_content
        super().update(instance=instance, validated_data=validated_data)
        return instance
    