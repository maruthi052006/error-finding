from django import forms
from .models import CustomUser
from events.models import Team

class TeamRegistrationForm(forms.ModelForm):
    # User fields
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}), required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}), required=True, label="Confirm Password")
    
    # Team fields
    team_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    member1_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    member1_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    member1_roll = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    
    member2_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    member2_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    member2_roll = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        # Check if team name is unique
        team_name = cleaned_data.get("team_name")
        if team_name and Team.objects.filter(name=team_name).exists():
            raise forms.ValidationError(f"Team '{team_name}' already exists.")

        return cleaned_data
