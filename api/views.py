from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Address, EMAUser

from .serializers import (ForgotPasswordSerializer, LogoutSerializer, ResetPasswordSerializer, SuperUserSerializer, 
ManagerSerializer, 
EmployeeSerializer,
EMAUserLoginSerializer, 
UsersListSerializer)

# Create your views here.

class CreateSuperUser(generics.CreateAPIView):
    serializer_class = SuperUserSerializer

class CreateManager(generics.CreateAPIView):
    serializer_class = ManagerSerializer

class CreateEmployee(generics.CreateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        requested_user = EMAUser.objects.get(id=request.user.id)
        if requested_user.role != "Manager":
            response = {
                'status':status.HTTP_403_FORBIDDEN,
                'message':'User not authorized to register Employee'
            }
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        
        else:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

                response = {
                    'status':status.HTTP_200_OK,
                    'message':'Employee registered successfully',
                    'user_details':serializer.data
                }

                return Response(response, status=status.HTTP_200_OK)

class EMAUserLogin(generics.GenericAPIView):
    serializer_class = EMAUserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class UsersList(generics.ListAPIView):
    serializer_class = UsersListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        requested_user = EMAUser.objects.get(id=request.user.id)
        if requested_user.role != "SuperUser":
            response = {
                'status':status.HTTP_403_FORBIDDEN,
                'message':'Unauthorised request'
            }
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        
        else:
            users = EMAUser.objects.all()
            serializer = self.serializer_class(users, many=True)

            response = {
                'status':status.HTTP_200_OK,
                'message':'Users fetched successfully',
                'users':serializer.data
            }

            return Response(response, status=status.HTTP_200_OK)

class Employees(generics.ListAPIView):
    serializer_class = UsersListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        requested_user = EMAUser.objects.get(id=request.user.id)
        if requested_user.role != "Manager":
            response = {
                'status':status.HTTP_403_FORBIDDEN,
                'message':'Unauthorised request'
            }
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        
        else:
            employees = EMAUser.objects.filter(role="Employee")
            serializer = self.serializer_class(employees, many=True)

            if employees.count() >= 1:
                response = {
                    'status':status.HTTP_200_OK,
                    'message':'Employees fetched successfully',
                    'employees':serializer.data
                }

                return Response(response, status=status.HTTP_200_OK)
            
            else: return Response({'message':'No employees found'},status=status.HTTP_404_NOT_FOUND)

class RetrieveUpdateDestroyEmployee(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EMAUser.objects.filter(id=self.kwargs['pk'], role="Employee")

    def get(self, request, *args, **kwargs):
        requested_user = EMAUser.objects.get(id=request.user.id)
        if requested_user.role != "Manager":
            response = {
                'status':status.HTTP_403_FORBIDDEN,
                'message':'Unauthorised request'
            }
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        else:
            employee = EMAUser.objects.get(id=self.kwargs['pk'], role="Employee")
            if employee:
                serializer = self.serializer_class(employee)

                response = {
                    'status':status.HTTP_200_OK,
                    'message':'Employee retrieved successfully',
                    'employee':serializer.data
                }

                return Response(response, status = status.HTTP_200_OK)
            else: Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        requested_user = EMAUser.objects.get(id=request.user.id)
        if requested_user.role != "Manager":
            response = {
                'status':status.HTTP_403_FORBIDDEN,
                'message':'Unauthorised request'
            }
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        
        else:
            instance = self.get_object()
            serializer = self.serializer_class(instance, data=request.data, partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

                response = {
                    'status':status.HTTP_200_OK,
                    'message':'Employee updated successfully',
                    'employee':serializer.data
                }

                return Response(response, status = status.HTTP_200_OK)
            else: return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        requested_user = EMAUser.objects.get(id=request.user.id)
        if requested_user.role != "Manager":
            response = {
                'status_code': status.HTTP_403_FORBIDDEN,
                'message': 'Unauthorised request'
            }
            return Response(response, status.HTTP_403_FORBIDDEN)
        else:
            employee_id = self.kwargs["pk"]
            employee = EMAUser.objects.filter(id=employee_id, role='Employee')

            if employee:
                employee.delete()
                Address.objects.filter(id=employee_id).delete()
                return Response({'message': 'Employee deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

            else: return Response({'message': 'Employee not found'}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPassword(generics.UpdateAPIView):
    serializer_class = ForgotPasswordSerializer

    def get_queryset(self):
        return EMAUser.objects.filter(id=self.kwargs['pk'])

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        data = request.data
        
        if user.email == data.get('email'):
            serializer = self.serializer_class(user, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                response = {
                    'status_code': status.HTTP_200_OK,
                    'message': 'Password reset successful. New password is sent to your email address'
                }
                return Response(response, status=status.HTTP_200_OK)
            else: return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else: return Response({'message':'Incorrect email'}, status=status.HTTP_401_UNAUTHORIZED)

class ResetPassword(generics.UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EMAUser.objects.filter(id=self.kwargs['pk'])

    def patch(self, request, *args, **kwargs):
        current_user = self.get_object()
        data = request.data

        serializer = self.serializer_class(current_user, data=data, context={'request': request}, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            response = {
                    'status_code': status.HTTP_200_OK,
                    'message': 'Password reset successful'
                }

            return Response(response, status=status.HTTP_200_OK)

        else: return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Logout(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)