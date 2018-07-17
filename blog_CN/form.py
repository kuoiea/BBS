#!/usr/bin/env python
# -*-coding:UTF-8 -*-

import re
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django import forms
from django.forms import widgets


class UserForm(forms.Form):
    name=forms.CharField(error_messages={"required":"该字段不能为空"})
    pwd=forms.CharField(error_messages={"required":"该字段不能为空"})
    r_pwd = forms.CharField(error_messages={"required":"该字段不能为空"})
    email = forms.EmailField(error_messages={"required":"该字段不能为空"})
    tel = forms.CharField(error_messages={"required":"该字段不能为空"})

    def clean_name(self):
        val = self.cleaned_data.get("name")
        if not val.isdigit():
            return val
        else:
            raise ValidationError("用户名不能是纯数字")

    def clean_email(self):
        val = self.cleaned_data.get("email")
        if re.match('^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$',val):
            return val
        else:
            raise ValidationError("邮箱格式不正确")

    def clean_tel(self):
        val = self.cleaned_data.get("tel")

        if re.match('(^(/d{3,4}-)?/d{7,8})$|(13[0-9]{9})',val):
            return val
        else:
            raise ValidationError("手机号格式不正确")

    def clean(self):
        pwd = self.cleaned_data.get("pwd")
        r_pwd = self.cleaned_data.get("r_pwd")
        if pwd and r_pwd and pwd != r_pwd:
            raise ValidationError("两次密码不一致")
        else:
            return self.cleaned_data








