from django import forms

class BarcodeForm(forms.Form):
    image = forms.ImageField(label="Cargar imagen del código de barras")
