from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from .models import StudySession, UserInterest
import numpy as np
import os

def get_tfidf_recommendations(user):
    # recommendations using TF-IDF and cosine similarity
    try:
        user_interest = UserInterest.objects.get(user=user)
        user_interests = user_interest.interests
    except UserInterest.DoesNotExist:
        recent_sessions = StudySession.objects.all().order_by('-created_at')[:5]
        return [(session, 0.5) for session in recent_sessions]
    
    if not user_interests.strip():
        recent_sessions = StudySession.objects.all().order_by('-created_at')[:5]
        return [(session, 0.5) for session in recent_sessions]
    
    # Get all sessions
    all_sessions = StudySession.objects.all()
    if not all_sessions:
        return []
    
    # Prepare data for TF-IDF
    session_documents = []
    session_ids = []
    
    for session in all_sessions:
        # Clean and prepare session tags BOW ko part ho
        session_tags = [tag.strip().lower() for tag in session.tags.split(",") if tag.strip()]
        session_doc = " ".join(session_tags)
        session_documents.append(session_doc)
        session_ids.append(session.id)
    
    user_interest_list = [interest.strip().lower() for interest in user_interests.split(",") if interest.strip()]
    user_doc = " ".join(user_interest_list)
    
    # TF-IDF vectors create gareko
    vectorizer = TfidfVectorizer()
    
    try:
        tfidf_matrix = vectorizer.fit_transform(session_documents)
        
        # Transform user interests
        user_vector = vectorizer.transform([user_doc])
        
        # Calculate cosine similarity (0-1 range return grxa)
        cosine_similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
        
        # session lae pair grxa with their similarity scores (0-1 range)
        session_scores = list(zip(all_sessions, cosine_similarities))
        
        scored_sessions = [(session, score) for session, score in session_scores if score > 0]
        scored_sessions.sort(key=lambda x: x[1], reverse=True)
        
        return scored_sessions[:10]
        
    except Exception as e:
        print(f"TF-IDF calculation error: {e}")
        return get_recommendations_simple(user)

def get_recommendations_simple(user):
    try:
        user_interest = UserInterest.objects.get(user=user)
        user_interests = [interest.strip().lower() for interest in user_interest.interests.split(",") if interest.strip()]
    except UserInterest.DoesNotExist:
        recent_sessions = StudySession.objects.all().order_by('-created_at')[:5]
        return [(session, 0.5) for session in recent_sessions]
    
    if not user_interests:
        recent_sessions = StudySession.objects.all().order_by('-created_at')[:5]
        return [(session, 0.5) for session in recent_sessions]
    
    scored_sessions = []
    all_sessions = StudySession.objects.all()
    
    for session in all_sessions:
        session_tags = [tag.strip().lower() for tag in session.tags.split(",")]
        score = 0
        
        for interest in user_interests:
            if interest in session_tags:
                score += 3
            for tag in session_tags:
                if interest in tag:
                    score += 1
                    break
            for tag in session_tags:
                if tag in interest:
                    score += 1
                    break
        
        if score > 0:
            # Normalize to 0-1 range (assuming max possible score is around 10)
            normalized_score = min(score / 10.0, 1.0)
            scored_sessions.append((session, normalized_score))
    
    scored_sessions.sort(key=lambda x: x[1], reverse=True)
    return scored_sessions[:10]

def get_recommendations(user):
    # main function ho hae returns sessions with 0-1 similarity scores
    result = get_tfidf_recommendations(user)
    if result and isinstance(result[0], StudySession):
        return [(session, 0.5) for session in result]
    return result