from django.contrib import admin

# Customize the admin site header and link to the new dashboard
admin.site.site_header = 'OpenBazar Admin'
admin.site.site_title = 'OpenBazar Admin'
admin.site.index_title = 'Administration'
# Add a quick link from the admin header logo to the modern dashboard
admin.site.site_url = '/dashboard/'
