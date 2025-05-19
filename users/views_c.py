from rest_framework.views import APIView
from rest_framework.response import Response

# Create test 

class HelloWorldView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):  
        return Response({"message": "Hello, world!"})  
    
