from .models import Employee, MedicineAdministration
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, get_object_or_404, redirect
from .models import Shiiregyosha
from .forms import ShiiregyoshaEditForm
from .forms import CapitalSearchForm
from django.contrib import messages
from .models import Patient, Medicine
from .forms import PatientSearchForm, MedicineForm


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            employee = Employee.objects.get(empfname=username)
            if employee.emprole == 1:
                # 管理者はハッシュ化されていないパスワードを使用
                if password == employee.emppaswd:
                    request.session['employee_id'] = employee.empid
                    request.session['employee_role'] = employee.emprole
                    return redirect('admin_home')
                else:
                    messages.error(request, 'Invalid password')
            else:
                # その他のユーザーはハッシュ化されたパスワードを使用
                if check_password(password, employee.emppaswd):
                    request.session['employee_id'] = employee.empid
                    request.session['employee_role'] = employee.emprole
                    if employee.emprole == 2:
                        return redirect('doctor_home')
                    elif employee.emprole == 3:
                        return redirect('uketuke_home')
                else:
                    messages.error(request, 'Invalid password')
        except Employee.DoesNotExist:
            messages.error(request, 'Employee does not exist')

    return render(request, 'kadai1/login.html')



def is_admin(user):
    return user.is_staff

def logout_view(request):
    return render(request, 'kadai1/logout.html')

def register_employee(request):
    if request.method == 'POST':
        empid = request.POST['empid']
        empfname = request.POST['empfname']
        emplname = request.POST['emplname']
        emppaswd = request.POST['emppaswd']
        password_confirm = request.POST['password_confirm']
        emprole = request.POST['emprole']

        # パスワード確認
        if emppaswd != password_confirm:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                emprole = int(emprole)
                if emprole not in [1, 2, 3]:
                    messages.error(request, 'Role must be 1, 2, or 3.')
                else:
                    # 管理者はハッシュ化しない、それ以外はハッシュ化
                    if emprole == 1:
                        hashed_password = emppaswd
                    else:
                        hashed_password = make_password(emppaswd)
                    Employee.objects.create(
                        empid=empid,
                        empfname=empfname,
                        emplname=emplname,
                        emppaswd=hashed_password,
                        emprole=emprole
                    )
                    messages.success(request, 'Employee registered successfully.')
                    return redirect('register_employee')
            except Exception as e:
                messages.error(request, f'Error: {e}')

    return render(request, 'admin_home/register_employee.html')

def supplier_edit(request):
    return render(request, 'admin_home/supplier_edit.html')

def patient_search(request):
    return render(request, 'doctor_home/patient_search.html')



def receptionist_home(request):
    return render(request, 'uketuke_home/receptionist_home.html')

def change_employee_password(request):
    return render(request, 'uketuke_home/change_employee_password.html')

def register_patient(request):
    return render(request, 'uketuke_home/register_patient.html' )

def change_patient_insurance(request):
    return render(request, 'uketuke_home/change_patient_insurance.html')

def search_patient_by_name(request):
    return render(request, 'uketuke_home/search_patient_by_name.html')

def shiiregyosha_list(request):
    shiiregyosha_list = Shiiregyosha.objects.all()
    return render(request, 'admin_home/supplier_list.html', {'shiiregyosha_list': shiiregyosha_list})

def supplier_listhe(request):
    return render(request, 'admin_home/supplier_list.html')

def edit_supplier(request, pk):
    supplier = get_object_or_404(Shiiregyosha, pk=pk)
    if request.method == 'POST':
        form = ShiiregyoshaEditForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_edit_confirm', pk=supplier.pk)
    else:
        form = ShiiregyoshaEditForm(instance=supplier)
    return render(request, 'admin_home/supplier_edit.html', {'form': form, 'supplier': supplier})

def edit_supplier_confirm(request, pk):
    supplier = get_object_or_404(Shiiregyosha, pk=pk)
    return render(request, 'admin_home/supplier_edit_confirm.html', {'supplier': supplier})

def edit_supplier(request, pk):
    try:
        supplier = get_object_or_404(Shiiregyosha, pk=pk)
    except Shiiregyosha.DoesNotExist:
        return render(request, 'admin_home/error.html', {'error_message': '仕入れ先が見つかりませんでした。'})

    if request.method == 'POST':
        form = ShiiregyoshaEditForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_edit_confirm', pk=supplier.pk)
    else:
        form = ShiiregyoshaEditForm(instance=supplier)
    return render(request, 'admin_home/supplier_edit.html', {'form': form, 'supplier': supplier})

def capital_search(request):
    if request.method == 'POST':
        form = CapitalSearchForm(request.POST)
        if form.is_valid():
            capital = form.cleaned_data['capital']
            results = Shiiregyosha.objects.filter(shihonkin__gte=capital)
            if results.exists():
                return render(request, 'admin_home/capital_search_results.html', {'form': form, 'results': results, 'capital': capital})
            else:
                message = '該当する仕入れ先はありません。'
                return render(request, 'admin_home/capital_search.html', {'form': form, 'message': message})
    else:
        form = CapitalSearchForm()
    return render(request, 'admin_home/capital_search.html', {'form': form})


def change_password(request):
    if 'employee_id' not in request.session:
        messages.error(request, 'ログインが必要です。')
        return redirect('login')

    employee = get_object_or_404(Employee, empid=request.session['employee_id'])

    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if not check_password(current_password, employee.emppaswd):
            messages.error(request, '現在のパスワードが正しくありません。')
        elif new_password != confirm_password:
            messages.error(request, '新しいパスワードが一致しません。')
        else:
            employee.emppaswd = make_password(new_password)
            employee.save()
            messages.success(request, 'パスワードが変更されました。')
            return redirect('password_change_done')

    return render(request, 'kadai1/password_change.html')

def admin_change_password(request, user_id=None):
    if 'employee_id' not in request.session or request.session.get('employee_role') != 1:
        messages.error(request, 'この操作は許可されていません。')
        return redirect('login')

    if user_id:
        user = get_object_or_404(Employee, empid=user_id)
    else:
        user = get_object_or_404(Employee, empid=request.session['employee_id'])

    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if new_password != confirm_password:
            messages.error(request, '新しいパスワードが一致しません。')
        else:
            if user.emprole == 1:
                user.emppaswd = new_password
            else:
                user.emppaswd = make_password(new_password)
            user.save()
            messages.success(request, 'パスワードが変更されました。')
            return render(request, 'kadai1/admin_password_change_done.html', {'user': user})

    return render(request, 'kadai1/admin_password_change.html', {'user': user})

def admin_home(request):
    if 'employee_id' not in request.session or request.session.get('employee_role') != 1:
        messages.error(request, 'ログインが必要です。')
        return redirect('login')
    return render(request, 'kadai1/admin_home.html', {'user_id': request.session['employee_id']})

def doctor_home(request):
    if 'employee_id' not in request.session or request.session.get('employee_role') != 2:
        messages.error(request, 'ログインが必要です。')
        return redirect('login')
    return render(request, 'kadai1/doctor_home.html')

def uketuke_home(request):
    if 'employee_id' not in request.session or request.session.get('employee_role') != 3:
        messages.error(request, 'ログインが必要です。')
        return redirect('login')
    return render(request, 'kadai1/uketuke_home.html')


def admin_dashboard(request):
    if 'employee_id' not in request.session or request.session.get('employee_role') != 1:
        messages.error(request, 'ログインが必要です。')
        return redirect('login')

    query = request.GET.get('query')
    if query:
        employees = Employee.objects.filter(empid__icontains=query)
    else:
        employees = Employee.objects.all()

    return render(request, 'kadai1/admin_dashboard.html', {'employees': employees, 'query': query})


def doctor_patient_search(request):
    form = PatientSearchForm()
    results = None
    if request.method == 'POST':
        form = PatientSearchForm(request.POST)
        if form.is_valid():
            patname = form.cleaned_data['patname']
            results = Patient.objects.filter(patfname__icontains=patname) | Patient.objects.filter(patlname__icontains=patname)
            if not results.exists():
                messages.error(request, '該当する患者は見つかりませんでした。')
    return render(request, 'doctor_home/patient_search.html', {'form': form, 'results': results})

def receptionist_patient_search(request):

    form = PatientSearchForm()
    results = None
    if request.method == 'POST':
        form = PatientSearchForm(request.POST)
        if form.is_valid():
            patname = form.cleaned_data['patname']
            results = Patient.objects.filter(patfname__icontains=patname) | Patient.objects.filter(patlname__icontains=patname)
            if not results.exists():
                messages.error(request, '該当する患者は見つかりませんでした。')
    return render(request, 'uketuke_home/patient_search.html', {'form': form, 'results': results})


def doctor_medicine_instructions(request, patient_id):
    patient = Patient.objects.get(patid=patient_id)
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            request.session['medicine_data'] = form.cleaned_data
            return redirect('medicine_confirmation')
    else:
        form = MedicineForm()
    return render(request, 'doctor_home/medicine_instructions.html', {'form': form, 'patient': patient})


def medicine_confirmation(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirm':
            return redirect('process_confirmed')
        elif action == 'edit':
            return redirect('doctor_medicine_instructions')
        elif action == 'delete':
            del request.session['medicine_data']
            return redirect('doctor_medicine_instructions')

    medicine_data = request.session.get('medicine_data')
    if not medicine_data:
        return redirect('doctor_medicine_instructions')
    return render(request, 'doctor_home/medicine_confirmation.html', {'medicine_data': medicine_data})


def process_confirmed(request):
    medicine_data = request.session.get('medicine_data')
    if not medicine_data:
        return redirect('doctor_medicine_instructions')

    patient_id = medicine_data.get('patient')
    medicine_id = medicine_data.get('medicine')
    quantity = medicine_data.get('quantity')

    patient = Patient.objects.get(patid=patient_id)
    medicine = Medicine.objects.get(medicineid=medicine_id)

    MedicineAdministration.objects.create(patient=patient, medicine=medicine, quantity=quantity)

    messages.success(request, '処置が確定されました。')
    del request.session['medicine_data']
    return redirect('doctor_home')


def treatment_history(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        return redirect('treatment_history_detail', patient_id=patient_id)
    return render(request, 'doctor_home/treatment_history.html')


def treatment_history_detail(request, patient_id):
    patient = Patient.objects.get(patid=patient_id)
    treatments = MedicineAdministration.objects.filter(patient=patient)
    return render(request, 'doctor_home/treatment_history_detail.html', {'patient': patient, 'treatments': treatments})