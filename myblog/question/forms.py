from django import  forms
from question.models import Topic,Comment

class TopicForm(forms.Form):
    title = forms.CharField(label='标题',required=True)
    content = forms.CharField(label='内容',required=False)

    def clean_title(self):
        title = self.cleaned_data.get("title").strip()
        if len(title) < 3:
            raise forms.ValidationError("标题太短...")
        elif len(title) > 100:
            raise forms.ValidationError("标题太长...")
        else:
            return title

    def clean_content(self):
        content = self.cleaned_data.get("content").strip()
        if len(content) > 5000:
            raise forms.ValidationError("内容太长...")
        else:
            return content