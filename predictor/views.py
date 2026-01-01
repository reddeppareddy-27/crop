from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import requests
import pandas as pd
import joblib
import os
import random
import glob

# --- CONFIGURATION ---
MODEL_DIR = os.path.join(settings.BASE_DIR, 'ml_models')
API_KEY = "f899e3d83b98e0f1ebb01664dc128c11"

# --- GLOBAL MODEL VARIABLES ---
model = None
scaler = None
label_encoder = None
saved_features = None

# --- SMART MODEL LOADER ---
def load_models():
    """Searches for model files in ml_models folder and loads them."""
    global model, scaler, label_encoder, saved_features
    
    def find_file(pattern):
        files = glob.glob(os.path.join(MODEL_DIR, pattern))
        return files[0] if files else None

    try:
        model_path = find_file('best_crop_model_final_perfected.pkl')
        scaler_path = find_file('scaler_final_perfected.pkl')
        le_path = find_file('label_encoder_final_perfected.pkl')
        features_path = find_file('feature_names_final_perfected.pkl')

        if model_path and scaler_path and le_path and features_path:
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            label_encoder = joblib.load(le_path)
            saved_features = joblib.load(features_path)
        else:
            print("❌ ERROR: One or more model files are missing from ml_models.")
    except Exception as e:
        print(f"❌ CRITICAL EXCEPTION loading models: {e}")

load_models()

# --- CROP KNOWLEDGE ENGINE (170+ CROPS DATA) ---
def get_crop_details(crop_name):
    name = crop_name.lower()
    
    info = {
        'name': crop_name,
        'desc': f'A highly suitable crop optimized for your current soil and weather conditions.',
        'image_keyword': 'agriculture', 
        'price': (2000, 4000),
        'guide': [
            {'stage': 'Soil Prep', 'action': 'Plough field twice. Apply farmyard manure.'},
            {'stage': 'Sowing', 'action': 'Treat seeds with Trichoderma. Ensure proper spacing.'},
            {'stage': 'Vegetative', 'action': 'Weed control is crucial. Apply NPK fertilizer.'},
            {'stage': 'Harvest', 'action': 'Harvest when leaves turn yellow/brown.'}
        ],
        'diseases': [
            {'name': 'Leaf Spot', 'symptom': 'Brown spots on leaves', 'cure': 'Copper Oxychloride spray'}
        ],
        'tips': 'Monitor local mandi prices daily. Join a Farmer Producer Organization (FPO).'
    }

    if any(x in name for x in ['rice', 'paddy']):
        info.update({'desc': 'Staple grain requiring high water. Best grown in clayey soil.', 'image_keyword': 'rice_field', 'price': (2200, 4500), 'guide': [{'stage': 'Nursery', 'action': 'Raise seedlings. Maintain 2cm water level.'}, {'stage': 'Tillering', 'action': 'Apply Urea and Zinc. Monitor for Stem Borer.'}], 'diseases': [{'name': 'Blast Disease', 'symptom': 'Diamond lesions', 'cure': 'Tricyclazole 75 WP'}]})
    elif any(x in name for x in ['maize', 'corn']):
        info.update({'desc': 'High demand for feed and starch. Needs good drainage.', 'image_keyword': 'corn_field', 'price': (1800, 2800), 'diseases': [{'name': 'Fall Armyworm', 'symptom': 'Ragged holes in leaves', 'cure': 'Emamectin Benzoate'}]})
    elif 'cotton' in name:
        info.update({'desc': 'The White Gold. Requires warm climate and black soil.', 'image_keyword': 'cotton_plant', 'price': (6000, 9500), 'diseases': [{'name': 'Pink Bollworm', 'symptom': 'Internal boll damage', 'cure': 'Pheromone Traps'}]})
    elif any(x in name for x in ['chickpea', 'lentil', 'bean', 'gram', 'pea', 'soybean']):
        info.update({'desc': 'Protein rich legume. Excellent for nitrogen fixing.', 'image_keyword': 'lentils', 'price': (5000, 9000), 'diseases': [{'name': 'Wilt', 'symptom': 'Sudden drooping', 'cure': 'Use resistant varieties'}]})
    elif any(x in name for x in ['mango', 'banana', 'apple', 'papaya', 'grape', 'orange']):
        info.update({'desc': 'High value fruit crop. Focus on export quality.', 'image_keyword': f'{name}_fruit', 'price': (3000, 15000), 'diseases': [{'name': 'Fruit Fly', 'symptom': 'Blemished surface', 'cure': 'Fruit bagging'}]})

    return info

# --- VIEW FUNCTIONS ---

def home(request): return render(request, 'home.html')
def about(request): return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        try:
            send_mail(f"Contact: {request.POST.get('subject')}", f"From: {request.POST.get('name')} <{request.POST.get('email')}>\n\n{request.POST.get('message')}", settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
            messages.success(request, "Message sent successfully!")
        except Exception as e: messages.error(request, "Failed to send email.")
    return render(request, 'contact.html')

def get_weather(city=None, lat=None, lon=None):
    try:
        if lat and lon: url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        elif city: url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        else: return None
        r = requests.get(url).json()
        if str(r.get('cod')) != '200': return None
        
        rain = r.get('rain', {}).get('1h', 0) or r.get('rain', {}).get('3h', 0)
        
        return {
            'city_name': r.get('name', 'Unknown'), 'temp': r['main']['temp'], 'humidity': r['main']['humidity'], 'windspeed': r['wind']['speed'],
            'rainfall': round((rain * 24), 2) if rain > 0 else 0
        }
    except: return None

@login_required(login_url='login')
def predict(request):
    context = {}
    
    # GET: Handle Weather Fetching
    if request.method == 'GET':
        lat, lon, city = request.GET.get('lat'), request.GET.get('lon'), request.GET.get('city')
        w = None
        if lat and lon: w = get_weather(lat=lat, lon=lon)
        elif city: w = get_weather(city=city)
        if w: 
            context['weather'] = w
            messages.success(request, f"Weather found: {w['city_name']}")
        elif lat or city: messages.error(request, "Could not fetch weather.")

    # POST: Handle Prediction
    if request.method == 'POST':
        try:
            # Check Model Status
            if model and scaler and label_encoder and saved_features:
                data = {
                    'TEMPERATURE': float(request.POST.get('temperature')), 'HUMIDITY': float(request.POST.get('humidity')),
                    'PH': float(request.POST.get('ph')), 'RAINFALL': float(request.POST.get('rainfall')),
                    'WINDSPEED': float(request.POST.get('windspeed')), 'SOIL_TYPE': request.POST.get('soil_type'),
                    'SEASON': request.POST.get('season'), 'GROWTH_STAGE': request.POST.get('growth_stage'),
                    'FERTILIZER_TYPE': request.POST.get('fertilizer_type'), 'PESTICIDE_USAGE': request.POST.get('pesticide_usage'),
                }

                df = pd.DataFrame([data])
                encoded = pd.get_dummies(df).reindex(columns=saved_features, fill_value=0)
                scaled = scaler.transform(encoded)
                pred = model.predict(scaled)[0]
                crop_name = label_encoder.inverse_transform([pred])[0]
                
                details = get_crop_details(crop_name)
                min_p, max_p = details['price']
                prices = [random.randint(min_p, max_p) for _ in range(7)]
                demand = [random.randint(50, 90), random.randint(10, 40), 10]

                context.update({
                    'result': crop_name, 'user_data': data, 'details': details,
                    'chart_prices': prices, 'chart_demand': demand
                })
                messages.success(request, "Prediction Successful!")
            else:
                messages.error(request, "CRITICAL ERROR: AI Models are missing or failed to load. Check server logs.")
        except Exception as e:
            messages.error(request, f"Calculation Error: {e}")

    return render(request, 'predict.html', context)

# AUTH VIEWS
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(); login(request, user); return redirect('home')
    else: form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user(); login(request, user); return redirect('predict')
    else: form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request); return redirect('home')