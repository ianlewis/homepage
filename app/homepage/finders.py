import os
from django.contrib.staticfiles.finders import AppDirectoriesFinder
from django.contrib.staticfiles.storage import AppStaticStorage

class AppMediaStorage(AppStaticStorage):
    source_dir = 'media'

    def get_location(self, app_root):
        """
        Given the app root, return the location of the static files of an app,
        by default 'static'. We special case the admin app here since it has
        its static files in 'media'.
        """
        if self.app_module == 'grappelli':
            return os.path.join(app_root, 'static')
        return os.path.join(app_root, self.source_dir)

class AppMediaDirectoriesFinder(AppDirectoriesFinder):
    storage_class = AppMediaStorage 
