import requests
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Blog
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from .serializers import BlogSerializer
from .utils import validate_password
import json

# Create your views here.

def getallnews(request):
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=059ab6e091d5403bb1663c371f9d3475"
    
    try:
        # Send the GET request to fetch data
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('articles', [])
            
            # Filter articles where 'id' is missing
            articles = [article for article in articles if article["source"].get('id')]  # Filter articles with 'id'
        else:
            articles = []
            messages.error(f"Error fetching news: {response.status_code}")
    except requests.exceptions.RequestException as e:
        # Log any exceptions that occur during the request
        articles = []
        messages.error(f"Error during request: {e}")
    
    # Render the news page with the filtered articles data
    return render(request, 'news.html', {"news": articles})


def news_detail(request, id):
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=059ab6e091d5403bb1663c371f9d3475"
    
    try:
        # Send the GET request to fetch data
        response = requests.get(url)
        
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('articles', [])
            
            # Find the article with the matching id
            article = next((article for article in articles if article["source"].get('id') == id), None)
            
            if article is None:
                # If article is not found, render an error message or 404
                return render(request, '404.html')
            
        else:
            article = None
            messages.error(f"Error fetching news: {response.status_code}")
    except requests.exceptions.RequestException as e:
        article = None
        messages.error(f"Error during request: {e}")
    
    # Render the news detail page with the specific article
    return render(request, 'detail-news.html', {"article": article})


@login_required
def home(request):
    try:
        all_blogs=Blog.objects.all().order_by('-created_at')
        return render(request,'home.html',{"blogs":all_blogs})
    except Blog.DoesNotExist:
        messages.error(request,"No Blog Found.")
    
    return render(request,'home.html')


def login_user(request):
    if request.user.is_authenticated:
        messages.error(request,"you are already logged In")
        return redirect('home')
    
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        
        messages.error(request,"Invalid Username or Password")
    
    return render(request,"login.html")


def register_user(request):
    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        
        # Password validation
        elif not validate_password(password):
            messages.error(
                request,
                "Password must be at least 8 characters long, include an uppercase letter, "
                "a lowercase letter, a number, and a special character."
            )
        
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
        
        else:
            user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name
            )

            user.set_password(password)
            user.save()

            messages.success(request, "Registration successful!")
            return redirect('login_user')

    return render(request, 'register.html')


def logout_user(request):
    if request.method=="POST":
        if not request.user.is_authenticated:
            messages.error(request,"Not Logged In")
            return redirect('login_user')
        
        logout(request)

    return redirect('login_user')


def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "forgot-password.html")

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password reset successfully. You can now log in.")
            return redirect("login_user")  # Change to your login page URL name
        except User.DoesNotExist:
            messages.error(request, "User not found.")
    
    return render(request, "forgot-password.html")


@login_required
def create_blog(request):
    if request.method=="POST":
        title=request.POST.get('title')
        body=request.POST.get('body')
        coverimage=request.FILES.get('coverimage')

        if not title or not body or not coverimage:
            messages.error("Must full all Required Fields.")
            return render(request,'create-blog.html')

        blog=Blog.objects.create(
            author=request.user,
            title=title,
            body=body,
            coverimage=coverimage
            )
        
        if blog is None:
            messages.error("something went wrong.")
            return render(request,'create-blog.html')
        
        messages.success(request, "Blog created successfully!")
        return redirect('home')
    
    return render(request,'create-blog.html')
        

@login_required
def get_user_blog(request):
    try:
        all_user_blog=Blog.objects.filter(author=request.user)

        return render(request,'user-blogs.html',{"blogs":all_user_blog})
    
    except Blog.DoesNotExist:
        messages.info("No Blog Created.")
        return render(request,'user-blogs.html')


def single_blog(request,id):
        blog=get_object_or_404(Blog,id=id)

        return render(request,'single-blog.html',{"blog":blog})


@login_required
def edit_blog(request, id):
    blog = get_object_or_404(Blog, id=id)

    if blog.author != request.user:
        messages.error(request, "You are not authorized to edit this blog.")
        return redirect('single_blog', id=id)

    if request.method == "POST":
        title = request.POST.get('title')
        body = request.POST.get('body')
        coverimage = request.FILES.get('coverimage')

        # Ensure at least one field is updated
        if not title and not body and not coverimage:
            messages.error(request, "No updates found.")
            return render(request, 'edit-blog.html', {"blog": blog})

        if title:
            blog.title = title
        if body:
            blog.body = body
        if coverimage:
            blog.coverimage = coverimage

        blog.save()
        messages.success(request, "Blog updated successfully!")
        return redirect('single_blog', id=id)

    return render(request, 'edit-blog.html', {"blog": blog})
    

@login_required
def delete_blog(request, id):
    blog = get_object_or_404(Blog, id=id)

    if blog.author != request.user:
        messages.error(request, "You are not authorized to delete this blog.")
        return redirect('single_blog', id=id)

    if request.method == "POST":
        blog.delete()
        messages.success(request, "The blog has been deleted successfully.")
        return redirect('home')  

    return render(request, 'delete-blog.html', {"blog": blog})


class BlogView(APIView):
    permission_classes = [IsAdminUser]  # Only admin can access this API

    def get(self, request):
        # List all blogs
        blogs = Blog.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create a new blog
        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # Set the logged-in user as the author
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Update an existing blog
        try:
            # Assuming the ID is sent in the body as JSON
            data = json.loads(request.body)
            blog_id = data.get('id')
            blog = Blog.objects.get(pk=blog_id)
            serializer = BlogSerializer(blog, data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Blog.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return Response({"detail": "Invalid JSON body."}, status=status.HTTP_400_BAD_REQUEST)


class BlogDeleteView(APIView):
    permission_classes = [IsAdminUser]  # Only admin can delete

    def delete(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
            blog.delete()
            return Response({"message": "Blog deleted successfully"}, status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)






