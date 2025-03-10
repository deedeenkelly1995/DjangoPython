from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Todo
from .serializers import TodoSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsOwner
from rest_framework.permissions import IsAuthenticated

class TodoListApiView(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        todos = Todo.objects.filter(user=request.user.id)
        serializer = TodoSerializer(todos, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)
        print(request.user)
        print(todos)
        # Custom response
        custom_data = {
            'count': todos.count(),
            'results': serializer.data,
            'message': 'List of todo items retrieved successfully'
        }
        return Response(custom_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        data = {
            'task': request.data.get('task'), 
            'completed': request.data.get('completed'), 
            'user': request.user.id
        }
        serializer = TodoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TodoDetailApiView(APIView):
        # add permission to check if user is authenticated
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated, IsOwner]


        def get_object(self, todo_id, user_id):
            '''
            Helper method to get the object with given todo_id, and user_id
            '''
            try:
                return Todo.objects.get(id=todo_id, user = user_id)
            except Todo.DoesNotExist:
                return None

        # 3. Retrieve
        def get(self, request, todo_id, *args, **kwargs):
            '''
            Retrieves the Todo with given todo_id
            '''
            todo_instance = self.get_object(todo_id, request.user.id)
            if not todo_instance:
                return Response(
                    {"res": "Object with todo id does not exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = TodoSerializer(todo_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 4. Update
        def put(self, request, todo_id, *args, **kwargs):
            '''
            Updates the todo item with given todo_id if exists
            '''
            todo_instance = self.get_object(todo_id, request.user.id)
            if not todo_instance:
                return Response(
                    {"res": "Object with todo id does not exists"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            data = {
                'task': request.data.get('task'), 
                'completed': request.data.get('completed'), 
                'user': request.user.id
            }
            serializer = TodoSerializer(instance = todo_instance, data=data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 5. Delete
        def delete(self, request, todo_id, *args, **kwargs):
            '''
            Deletes the todo item with given todo_id if exists
            '''
            todo_instance = self.get_object(todo_id, request.user.id)
            if not todo_instance:
                return Response(
                    {"res": "Object with todo id does not exists"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            todo_instance.delete()
            return Response(
                {"res": "Object deleted!"},
                status=status.HTTP_200_OK
            )