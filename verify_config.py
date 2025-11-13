#!/usr/bin/env python
"""
Configuration verification script for Render deployment.
Run this before deploying to ensure everything is properly configured.
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Check if a file exists."""
    exists = Path(filepath).exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"{status} {filepath}")
    return exists

def check_env_var(var_name, required=True):
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    is_set = value is not None and value != ""
    status = "✅" if is_set else ("❌" if required else "⚠️")
    masked_value = "***" if is_set and "KEY" in var_name else (value if is_set else "Not set")
    print(f"{status} {var_name}: {masked_value}")
    return is_set

def main():
    print("\n" + "="*60)
    print("🔍 AutoParse Render Deployment Configuration Check")
    print("="*60 + "\n")
    
    all_good = True
    
    # Check required files
    print("📁 Required Files:")
    all_good &= check_file_exists("requirements.txt", required=True)
    all_good &= check_file_exists("build.sh", required=True)
    all_good &= check_file_exists("render.yaml", required=True)
    all_good &= check_file_exists("runtime.txt", required=True)
    all_good &= check_file_exists("manage.py", required=True)
    all_good &= check_file_exists("autoparse/settings.py", required=True)
    all_good &= check_file_exists("autoparse/wsgi.py", required=True)
    
    print("\n📄 Optional Files:")
    check_file_exists("README.md", required=False)
    check_file_exists("DEPLOYMENT.md", required=False)
    check_file_exists(".gitignore", required=False)
    
    # Check environment variables (for local testing)
    print("\n🔐 Environment Variables (for local development):")
    check_env_var("SECRET_KEY", required=False)
    check_env_var("DEBUG", required=False)
    check_env_var("ANTHROPIC_API_KEY", required=False)
    check_env_var("ALLOWED_HOSTS", required=False)
    
    # Check build.sh is executable
    print("\n🔧 File Permissions:")
    build_sh_path = Path("build.sh")
    if build_sh_path.exists():
        is_executable = os.access(build_sh_path, os.X_OK)
        status = "✅" if is_executable else "❌"
        print(f"{status} build.sh is executable")
        if not is_executable:
            print("   Run: chmod +x build.sh")
            all_good = False
    
    # Import check
    print("\n📦 Django Configuration:")
    try:
        # Set minimal env vars for checking
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autoparse.settings')
        os.environ.setdefault('SECRET_KEY', 'test-key-for-verification')
        
        import django
        print("✅ Django imports successfully")
        
        # Check if we can import settings
        from django.conf import settings
        print("✅ Settings module loads successfully")
        
        # Check critical settings
        print("\n⚙️  Critical Settings:")
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"✅ DATABASE: {list(settings.DATABASES.keys())}")
        print(f"✅ STATIC_ROOT: {settings.STATIC_ROOT}")
        
        # Check installed apps
        required_apps = ['rest_framework', 'candidates', 'corsheaders']
        print("\n📱 Required Apps:")
        for app in required_apps:
            is_installed = app in settings.INSTALLED_APPS
            status = "✅" if is_installed else "❌"
            print(f"{status} {app}")
            all_good &= is_installed
        
        # Check middleware
        required_middleware = [
            'whitenoise.middleware.WhiteNoiseMiddleware',
            'corsheaders.middleware.CorsMiddleware',
        ]
        print("\n🔗 Required Middleware:")
        for middleware in required_middleware:
            is_present = middleware in settings.MIDDLEWARE
            status = "✅" if is_present else "❌"
            print(f"{status} {middleware}")
            all_good &= is_present
            
    except Exception as e:
        print(f"❌ Error loading Django configuration: {e}")
        all_good = False
    
    # Summary
    print("\n" + "="*60)
    if all_good:
        print("✅ All critical checks passed! Ready for deployment.")
        print("\n📝 Next steps:")
        print("1. Commit and push your code to Git")
        print("2. Create a new Blueprint on Render")
        print("3. Set environment variables in Render dashboard")
        print("4. Deploy!")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

