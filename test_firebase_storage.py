"""
Test script to verify Firebase Storage connection and list your model files
Run this before starting the main API to ensure everything is configured correctly
"""

import firebase_admin
from firebase_admin import credentials, storage
import sys

# Configuration - UPDATE THESE!
FIREBASE_CREDS_PATH = 'firebase-credentials.json'
FIREBASE_STORAGE_BUCKET = 'ordernpickapp.firebasestorage.app' # Change to your project ID
STORAGE_FOLDER = 'SentimentalAnalysis'

def test_firebase_connection():
    """Test Firebase connection and list files"""
    print("=" * 60)
    print("Firebase Storage Connection Test")
    print("=" * 60)
    
    # Step 1: Initialize Firebase
    print("\n[1/3] Initializing Firebase...")
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_CREDS_PATH)
            firebase_admin.initialize_app(cred, {
                'storageBucket': FIREBASE_STORAGE_BUCKET
            })
        print("✓ Firebase initialized successfully")
    except FileNotFoundError:
        print("✗ Error: firebase-credentials.json not found!")
        print("  Download it from Firebase Console → Project Settings → Service Accounts")
        return False
    except Exception as e:
        print(f"✗ Firebase initialization failed: {e}")
        return False
    
    # Step 2: Access Storage
    print("\n[2/3] Connecting to Storage...")
    try:
        bucket = storage.bucket()
        print(f"✓ Connected to bucket: {bucket.name}")
    except Exception as e:
        print(f"✗ Storage connection failed: {e}")
        print(f"  Check if bucket name is correct: {FIREBASE_STORAGE_BUCKET}")
        return False
    
    # Step 3: List files in your folder
    print(f"\n[3/3] Listing files in '{STORAGE_FOLDER}/' folder...")
    try:
        blobs = bucket.list_blobs(prefix=STORAGE_FOLDER)
        files = []
        
        for blob in blobs:
            if not blob.name.endswith('/'):  # Skip folder entries
                files.append(blob.name)
                size_mb = blob.size / (1024 * 1024)
                print(f"  ✓ Found: {blob.name} ({size_mb:.2f} MB)")
        
        if not files:
            print(f"  ✗ No files found in '{STORAGE_FOLDER}/' folder!")
            print(f"  Make sure you uploaded your model files to Firebase Storage")
            return False
        
        print(f"\n✓ Found {len(files)} file(s) in Storage")
        
        # Check for required files
        print("\n[Verification] Checking required files...")
        required_files = ['emotion_model.h5', 'tokenizer.pkl']  # Update if your names differ
        
        for required in required_files:
            full_path = f"{STORAGE_FOLDER}/{required}"
            if any(full_path in f for f in files):
                print(f"  ✓ {required} - Found")
            else:
                print(f"  ✗ {required} - Missing")
                print(f"     Looking for: {full_path}")
                print(f"     Available files: {', '.join(files)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error listing files: {e}")
        return False

def download_test():
    """Test downloading a small file"""
    print("\n" + "=" * 60)
    print("Testing Download")
    print("=" * 60)
    
    try:
        bucket = storage.bucket()
        
        # Try to download tokenizer (usually smaller than model)
        test_file = f"{STORAGE_FOLDER}/tokenizer.pkl"
        print(f"\nAttempting to download: {test_file}")
        
        blob = bucket.blob(test_file)
        
        if not blob.exists():
            print(f"✗ File does not exist: {test_file}")
            return False
        
        print("  Downloading...")
        blob.download_to_filename('test_download.pkl')
        print("  ✓ Download successful!")
        print("  ✓ Saved as: test_download.pkl")
        
        # Clean up
        import os
        os.remove('test_download.pkl')
        print("  ✓ Test file deleted")
        
        return True
        
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return False

if __name__ == "__main__":
    print("\n🔍 Firebase Storage Verification Tool\n")
    
    # Test connection and list files
    connection_ok = test_firebase_connection()
    
    if connection_ok:
        # Test downloading
        download_ok = download_test()
        
        if download_ok:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("=" * 60)
            print("\nYou're ready to run the main API:")
            print("  python app.py")
            print("\n")
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("⚠️  Connection OK but download failed")
            print("=" * 60)
            print("\nCheck Firebase Storage permissions")
            sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("❌ CONNECTION FAILED")
        print("=" * 60)
        print("\nPlease fix the errors above and try again")
        sys.exit(1)
