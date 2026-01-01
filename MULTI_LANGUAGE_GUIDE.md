# Multi-Language Support Guide

## How to Add Multi-Language Support to Your Website

### Languages Currently Supported:
- 🇬🇧 English (en)
- 🇪🇸 Spanish (es)
- 🇮🇳 Hindi (hi)
- 🇫🇷 French (fr)
- 🇨🇳 Chinese (zh)

## How It Works:

1. **Translation File**: All translations are stored in `static/js/translations.js`

2. **Using Translations in HTML**:
   - Add `data-i18n="keyName"` attribute to any HTML element
   - Example: `<h1 data-i18n="homeTitle">Home Title</h1>`
   - The content will automatically translate when language is changed

3. **Language Switching**:
   - Language selector is in the navbar
   - Selection is saved in browser localStorage
   - Page automatically reloads with new language

## How to Add New Translations:

### Step 1: Add the key to `translations.js`
```javascript
const translations = {
    en: {
        myNewKey: 'English text here',
        // ... more keys
    },
    es: {
        myNewKey: 'Texto en español',
        // ... more keys
    },
    // ... more languages
};
```

### Step 2: Use in HTML
```html
<p data-i18n="myNewKey">English text here</p>
```

The text will automatically translate based on selected language!

## How to Add a New Language:

### Step 1: Add language object in `translations.js`
```javascript
const translations = {
    // ... existing languages
    pt: {  // Portuguese
        home: 'Página inicial',
        about: 'Sobre nós',
        // ... add all keys here
    }
};
```

### Step 2: Add option to language selector in `base.html`
```html
<select id="lang-selector" class="lang-selector" onchange="setLanguage(this.value)">
    <option value="en">English</option>
    <option value="es">Español</option>
    <option value="hi">हिन्दी</option>
    <option value="fr">Français</option>
    <option value="zh">中文</option>
    <option value="pt">Português</option>  <!-- Add this -->
</select>
```

## Key Features:

✅ **Persistent Selection**: Language choice saved in browser localStorage
✅ **Automatic Translation**: Just add `data-i18n` attribute to elements
✅ **No Backend Required**: All translations handled by JavaScript
✅ **Fast & Efficient**: Translations load instantly
✅ **Easy to Maintain**: All translations in one file
✅ **Professional UI**: Language selector in navbar with smooth animations

## Translation Keys Available:

### Navigation
- home, about, predict, contact, signIn, signUp, logout

### Home Page
- aiPoweredAgriculture, intelligentCropPrediction, startPrediction, learnMore
- whyChoose, experienceFuture, howItWorks, readyTransform, startNow

### Auth
- loginTitle, loginSubtitle, signInButton, signUpButton
- createAccount, dontHaveAccount, alreadyHaveAccount

### Other Pages
- contactUs, sendMessage, address, phone, businessHours, followUs
- aboutUs, ourMission, meetOurTeam, technologyStack

## Tips:

1. Always add translations for ALL languages before using the key
2. Use consistent key naming (camelCase)
3. Keep translations in the same order across all languages
4. Test with each language to ensure content displays properly
5. Check for text overflow in smaller screens

## Need More Languages?

You can add any language! Common ones:
- 🇩🇪 German (de)
- 🇯🇵 Japanese (ja)
- 🇮🇹 Italian (it)
- 🇵🇹 Portuguese (pt)
- 🇷🇺 Russian (ru)

Just follow the steps above!
