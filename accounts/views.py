import random
from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import User, PasswordResetOTP
from accounts.serializers import UserSerializer, ReqeustOTPSerializer, VerifyOTPSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    def patch(self,reqeust):
        serializer = UserSerializer(reqeust.user, data=reqeust.data, partial=True, context={"request": reqeust})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOTPView(APIView):
    def post(self,request):
        serializer = ReqeustOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        otp = f"{random.randint(1000, 9999)}"

        PasswordResetOTP.objects.create(user=user,otp=otp)


        #send email
        print(otp)
        # send_mail(
        #     "Your Password Reset OTP",
        #     f"Your OTP is {otp}. It expires in 1 minute.",
        #     "no-reply@yourapp.com",
        #     [email],
        #     fail_silently=False
        # )

        return Response({'message': f'OTP send to email {email}'})


class VerifyOTPView(APIView):
    def post(self,request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except PasswordResetOTP.DoesNotExist:
            return Response({"message": 'user not found'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_obj = PasswordResetOTP.objects.get(user=user,otp=otp,is_used=False)
        except PasswordResetOTP.DoesNotExist:
            return Response({"message": "OTP is invalid"})

        if otp_obj.is_expired():
            otp_obj.delete()
            return Response({"message": 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)


        #update password
        user.set_password(password)
        user.save()

        otp_obj.is_used = True
        otp_obj.save()

        otp_obj.delete()

        return Response({"detail": "Password reset successful"})
