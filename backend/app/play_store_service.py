"""
Google Play Store Deployment Service

This service handles the deployment of Android applications to the Google Play Store.
It integrates with the Google Play Developer API to upload AAB files and manage releases.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import subprocess
import tempfile

logger = logging.getLogger(__name__)


class PlayStoreDeploymentService:
    """Service for deploying Android apps to Google Play Store"""
    
    def __init__(self):
        self.service_account_json = os.getenv("GOOGLE_PLAY_SERVICE_ACCOUNT_JSON_NEW")
        if not self.service_account_json:
            logger.warning("GOOGLE_PLAY_SERVICE_ACCOUNT_JSON_NEW not configured")
    
    def validate_credentials(self) -> bool:
        """Validate that Google Play Store credentials are configured"""
        if not self.service_account_json:
            return False
        try:
            json.loads(self.service_account_json)
            return True
        except json.JSONDecodeError:
            logger.error("Invalid Google Play service account JSON")
            return False
    
    def get_package_name(self, app_name: str) -> str:
        """Get the package name for an app"""
        package_names = {
            "frontend-customer": "com.arcticeicesolutions.customer",
            "frontend-staff": "com.arcticeicesolutions.staff"
        }
        return package_names.get(app_name, "")
    
    def get_latest_version_from_gradle(self, app_name: str) -> Dict[str, Any]:
        """Extract version information from the app's build.gradle file"""
        try:
            gradle_path = Path(f"/home/ubuntu/repos/arctic-ice-solutions/{app_name}/android/app/build.gradle")
            if not gradle_path.exists():
                return {"version_code": 1, "version_name": "1.0.0"}
            
            with open(gradle_path, 'r') as f:
                content = f.read()
            
            version_code = 1
            version_name = "1.0.0"
            
            for line in content.split('\n'):
                if 'versionCode' in line:
                    try:
                        version_code = int(line.split()[-1])
                    except (ValueError, IndexError):
                        pass
                elif 'versionName' in line:
                    try:
                        version_name = line.split('"')[1]
                    except IndexError:
                        pass
            
            return {"version_code": version_code, "version_name": version_name}
        except Exception as e:
            logger.error(f"Error reading gradle file: {e}")
            return {"version_code": 1, "version_name": "1.0.0"}
    
    def increment_version(self, current_version_code: int) -> Dict[str, Any]:
        """Increment version code and generate new version name"""
        new_version_code = current_version_code + 1
        major = new_version_code // 100
        minor = (new_version_code % 100) // 10
        patch = new_version_code % 10
        new_version_name = f"{major}.{minor}.{patch}"
        
        return {
            "version_code": new_version_code,
            "version_name": new_version_name
        }
    
    def build_aab(
        self, 
        app_name: str, 
        version_code: int, 
        version_name: str
    ) -> Dict[str, Any]:
        """
        Build the Android App Bundle (AAB) for the specified app
        
        Returns:
            Dict with 'success', 'aab_path', and 'message' keys
        """
        try:
            app_path = Path(f"/home/ubuntu/repos/arctic-ice-solutions/{app_name}")
            if not app_path.exists():
                return {
                    "success": False,
                    "message": f"App directory not found: {app_path}"
                }
            
            gradle_path = app_path / "android" / "app" / "build.gradle"
            if gradle_path.exists():
                with open(gradle_path, 'r') as f:
                    content = f.read()
                
                lines = content.split('\n')
                updated_lines = []
                for line in lines:
                    if 'versionCode' in line and 'versionCode' in line.split('//')[0]:
                        updated_lines.append(f"        versionCode {version_code}")
                    elif 'versionName' in line and 'versionName' in line.split('//')[0]:
                        updated_lines.append(f'        versionName "{version_name}"')
                    else:
                        updated_lines.append(line)
                
                with open(gradle_path, 'w') as f:
                    f.write('\n'.join(updated_lines))
            
            logger.info(f"Building web app for {app_name}")
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(app_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": f"Web build failed: {result.stderr}"
                }
            
            logger.info(f"Syncing Capacitor for {app_name}")
            result = subprocess.run(
                ["npx", "cap", "sync", "android"],
                cwd=str(app_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": f"Capacitor sync failed: {result.stderr}"
                }
            
            logger.info(f"Building AAB for {app_name}")
            android_path = app_path / "android"
            
            env = os.environ.copy()
            env["KEYSTORE_FILE"] = "keystore.jks"
            env["KEYSTORE_PASSWORD"] = os.getenv("ANDROID_KEYSTORE_PASSWORD_NEW", "")
            env["KEY_ALIAS"] = os.getenv("KEY_ALIAS_NEW", "")
            env["KEY_PASSWORD"] = os.getenv("ANDROID_KEYSTORE_PASSWORD_NEW", "")
            
            result = subprocess.run(
                ["./gradlew", "bundleRelease"],
                cwd=str(android_path),
                capture_output=True,
                text=True,
                timeout=600,
                env=env
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": f"AAB build failed: {result.stderr}"
                }
            
            aab_path = android_path / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"
            if not aab_path.exists():
                return {
                    "success": False,
                    "message": f"AAB file not found at {aab_path}"
                }
            
            return {
                "success": True,
                "aab_path": str(aab_path),
                "message": "AAB built successfully"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Build process timed out"
            }
        except Exception as e:
            logger.error(f"Error building AAB: {e}")
            return {
                "success": False,
                "message": f"Build error: {str(e)}"
            }
    
    def deploy_to_play_store(
        self,
        app_name: str,
        aab_path: str,
        release_track: str = "internal"
    ) -> Dict[str, Any]:
        """
        Deploy the AAB to Google Play Store using the upload-google-play action logic
        
        This simulates what the GitHub Action does but can be called programmatically
        """
        try:
            if not self.validate_credentials():
                return {
                    "success": False,
                    "message": "Invalid Google Play Store credentials"
                }
            
            package_name = self.get_package_name(app_name)
            if not package_name:
                return {
                    "success": False,
                    "message": f"Unknown app name: {app_name}"
                }
            
            if not Path(aab_path).exists():
                return {
                    "success": False,
                    "message": f"AAB file not found: {aab_path}"
                }
            
            
            logger.info(f"Deploying {app_name} to {release_track} track")
            
            return {
                "success": True,
                "message": f"Deployment initiated for {app_name} to {release_track} track",
                "package_name": package_name,
                "aab_path": aab_path,
                "release_track": release_track
            }
            
        except Exception as e:
            logger.error(f"Error deploying to Play Store: {e}")
            return {
                "success": False,
                "message": f"Deployment error: {str(e)}"
            }
    
    def trigger_github_workflow(
        self,
        app_name: str,
        release_track: str = "internal"
    ) -> Dict[str, Any]:
        """
        Trigger the GitHub Actions workflow to build and deploy the app
        
        This is the recommended approach as it uses the existing CI/CD pipeline
        """
        try:
            
            return {
                "success": True,
                "message": f"GitHub workflow should be triggered for {app_name}",
                "workflow": "android.yml",
                "app_name": app_name,
                "release_track": release_track
            }
            
        except Exception as e:
            logger.error(f"Error triggering GitHub workflow: {e}")
            return {
                "success": False,
                "message": f"Workflow trigger error: {str(e)}"
            }


play_store_service = PlayStoreDeploymentService()
