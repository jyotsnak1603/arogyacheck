from .translations import TRANSLATIONS

def translations(request):
    # Detect the current language from the request (set by LocaleMiddleware)
    lang = getattr(request, 'LANGUAGE_CODE', 'en')
    
    # Extract the main locale (e.g., 'en-us' -> 'en')
    if '-' in lang:
        lang = lang.split('-')[0]
    
    # Fallback to English if translation is missing
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    return {
        't': t,
        'current_lang': lang
    }
