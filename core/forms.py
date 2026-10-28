from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Vehicle, Booking, Review


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name', 'battery_kwh', 'connector_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['vehicle', 'start_time', 'current_battery', 'target_battery']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        if user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[(i, f'{i} ⭐') for i in range(5, 0, -1)], coerce=int,
        widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Your experience (optional)'})
        }