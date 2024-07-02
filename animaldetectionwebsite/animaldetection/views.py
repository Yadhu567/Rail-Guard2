from django.shortcuts import render, redirect
from django.contrib import messages
from pymongo import MongoClient
from bson.objectid import ObjectId


client = MongoClient('mongodb://localhost:27017')
db = client['masters']
users_collection = db['users']

def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        
        if users_collection.find_one({"email": email}):
            messages.error(request, 'User with this email already exists.')
            return redirect('animaldetection:signup')
        
        user = {
            'name': name,
            'email': email,
            'password': password,
            'detections': []
        }
        users_collection.insert_one(user)
        messages.success(request, 'User created successfully. Please sign in.')
        return redirect('animaldetection:signin')
    
    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = users_collection.find_one({"email": email, "password": password})
        if user:
            request.session['user_id'] = str(user['_id']) 
            messages.success(request, 'Logged in successfully.')
            return redirect('animaldetection:lastdocument')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
            return redirect('animaldetection:signin')
    
    return render(request, 'signin.html')
def reset(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = users_collection.find_one({"email": email})
        if user:
            request.session['reset_user_id'] = str(user['_id'])
            return redirect('animaldetection:reset_password')
        else:
            messages.error(request, 'No user found with this email.')
            return redirect('animaldetection:reset')
    
    return render(request, 'reset.html')

def reset_password(request):
    if request.method == 'POST':
        user_id = request.session.get('reset_user_id')
        if not user_id:
            messages.error(request, 'No user to reset password for.')
            return redirect('animaldetection:reset')

        new_password = request.POST['new_password']
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"password": new_password}})
        del request.session['reset_user_id']
        messages.success(request, 'Password reset successfully. Please sign in.')
        return redirect('animaldetection:signin')
    
    return render(request, 'reset_password.html')

def lastdocument(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'You need to sign in first.')
        return redirect('animaldetection:signin')

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        messages.error(request, 'User not found.')
        return redirect('animaldetection:signin')

    if not user.get('detections'):
        messages.error(request, 'No detections found for this user.')
        return redirect('animaldetection:lastdocument')

    last_detection = user['detections'][-1]  

    context = {
        'document': last_detection,
    }
    return render(request, 'lastdocument.html', context)

def alldocuments(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'You need to sign in first.')
        return redirect('animaldetection:signin')

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        messages.error(request, 'User not found.')
        return redirect('animaldetection:signin')

    all_detections = user.get('detections', [])

    context = {
        'documents': all_detections,
    }
    return render(request, 'alldocuments.html', context)
