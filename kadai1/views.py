from django.utils.timezone import now

from .models import Employee, MedicineAdministration
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, get_object_or_404, redirect
from .models import Shiiregyosha
from .forms import ShiiregyoshaEditForm, PatientidSearchForm, SupplierForm
from .forms import CapitalSearchForm
from django.contrib import messages
from .models import Patient, Medicine
from .forms import PatientSearchForm, MedicineForm
from django.urls import reverse
import re
from .forms import PasswordChangeForm

def login_view(request):
    if request.method == 'POST':
        empid = request.POST['empid']
        password = request.POST['password']

        try:
            employee = Employee.objects.get(empid=empid)
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
            # empidの検証 (英数字のみ許可)
            if not re.match(r'^[a-zA-Z0-9]+$', empid):
                messages.error(request, 'IDには英数字を入力してください。')
            else:
                try:
                    # empidの重複チェック
                    if Employee.objects.filter(empid=empid).exists():
                        messages.error(request, 'そのIDは使えません。既に登録されています。')
                    else:
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
                                empid=empid,  # empidは文字列として保存
                                empfname=empfname,
                                emplname=emplname,
                                emppaswd=hashed_password,
                                emprole=emprole
                            )
                            messages.success(request, '登録しました。')
                            return redirect('register_employee')
                except Exception as e:
                    messages.error(request, f'Error: {e}')

    return render(request, 'admin_home/register_employee.html')

def supplier_edit(request, supplier_id):
    supplier = get_object_or_404(Shiiregyosha, pk=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, '仕入れ先情報が更新されました。')
            return redirect('shiiregyosha_list')
        else:
            messages.error(request, '入力に誤りがあります。')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'admin_home/supplier_edit.html', {'form': form, 'supplier': supplier})

def patient_search(request):
    return render(request, 'doctor_home/patient_search.html')


def shiiregyosha_list(request):
    try:
        shiiregyosha_list = Shiiregyosha.objects.all()
    except Exception as e:
        messages.error(request, '仕入れ先一覧の取得に失敗しました: {}'.format(str(e)))
        shiiregyosha_list = []

    return render(request, 'admin_home/supplier_list.html', {'shiiregyosha_list': shiiregyosha_list})

def supplier_listhe(request):
    return render(request, 'admin_home/supplier_list.html')

def edit_supplier(request, pk):
    supplier = get_object_or_404(Shiiregyosha, pk=pk)
    if request.method == 'POST':
        form = ShiiregyoshaEditForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, '仕入れ先情報が更新されました。')
            return redirect('supplier_edit_confirm', pk=supplier.pk)
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = ShiiregyoshaEditForm(instance=supplier)
    return render(request, 'admin_home/supplier_edit.html', {'form': form, 'supplier': supplier})

def supplier_edit_confirm(request, pk):
    supplier = get_object_or_404(Shiiregyosha, pk=pk)
    if request.method == 'POST':
        return redirect('edit_supplier', pk=supplier.pk)
    return render(request, 'admin_home/supplier_edit_confirm.html', {'supplier': supplier})
def capital_search(request):
    if request.method == 'POST':
        form = CapitalSearchForm(request.POST)
        if form.is_valid():
            capital = form.cleaned_data['capital']
            results = Shiiregyosha.objects.filter(shihonkin__gte=capital)
            if results.exists():
                return render(request, 'admin_home/capital_search_results.html', {'form': form, 'results': results, 'capital': capital})
            else:
                messages.error(request, '該当する仕入れ先はありません。')
        else:
            messages.error(request, '入力に誤りがあります。')
    else:
        form = CapitalSearchForm()
    return render(request, 'admin_home/capital_search.html', {'form': form})


def change_password(request):
    if 'employee_id' not in request.session:
        messages.error(request, 'ログインが必要です。')
        return redirect('login')

    employee = get_object_or_404(Employee, empid=request.session['employee_id'])

    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if new_password != confirm_password:
            messages.error(request, '新しいパスワードが一致しません。')
        else:
            employee.emppaswd = make_password(new_password)
            employee.save()
            messages.success(request, 'パスワードが変更されました。')

            if employee.emprole == 3:
                return redirect('password_change_u')
            elif employee.emprole == 2:
                return redirect('password_change_b')
            else:
                messages.error(request, '無効な役割です。')
                return redirect('login')

    return render(request, 'kadai1/password_change.html')

def password_change_b(request):
    return render(request, 'kadai1/password_home.html')

def password_change_u(request):
    return render(request, 'kadai1/password_homeuketuke.html')

def admin_change_password(request, user_id=None):
    if 'employee_id' not in request.session or request.session.get('employee_role') != 1:
        messages.error(request, 'この操作は許可されていません。')
        return redirect('login')

    if user_id:
        user = get_object_or_404(Employee, empid=user_id)
    else:
        user = get_object_or_404(Employee, empid=request.session['employee_id'])

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            if new_password != confirm_password:
                messages.error(request, '新しいパスワードが一致しません。')
            else:
                if user.emprole == 1:
                    user.emppaswd = new_password
                else:
                    user.emppaswd = make_password(new_password)
                user.save()
                messages.success(request, 'パスワードが変更されました。')
                return redirect('admin_dashboard')  # パスワード変更後のリダイレクト先
    else:
        form = PasswordChangeForm()

    return render(request, 'kadai1/admin_password_change.html', {'user': user, 'form': form})

def admin_home(request):
    if 'employee_id' not in request.session or request.session.get('employee_role') != 1:
        messages.error(request, 'ログインが必要です。')
        return redirect('login')
    return render(request, 'kadai1/admin_home.html', {'user_id': request.session['employee_id']})

def doctor_home(request):
    if 'employee_id' not in request.session or request.session.get('employee_role') != 2:
        messages.error(request, 'ログインが必要です。')
        return redirect('login')
    patients = Patient.objects.all()  # すべての患者を取得
    return render(request, 'kadai1/doctor_home.html', {'patients': patients})

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

    for employee in employees:
        employee.change_password_url = reverse('admin_change_password', args=[employee.empid])

    return render(request, 'kadai1/admin_dashboard.html', {'employees': employees, 'query': query})

def doctor_patientid_search(request):
    form = PatientidSearchForm(request.POST or None)
    results = None

    if request.method == 'POST' and form.is_valid():
        patient_id = form.cleaned_data['patient_id']
        try:
            patient = Patient.objects.get(patid=patient_id)
            results = [patient]
        except Patient.DoesNotExist:
            results = []

    context = {
        'form': form,
        'results': results,
    }
    return render(request, 'doctor_home/doctorid_patient_search.html', context)


def doctor_patient_search(request):
    form = PatientSearchForm()
    results = None
    if request.method == 'POST':
        form = PatientSearchForm(request.POST)
        if form.is_valid():
            patfname = form.cleaned_data['patfname']
            patlname = form.cleaned_data['patlname']

            # クエリセットの初期化
            results = Patient.objects.all()

            # 名前フィールドが入力された場合のフィルタリング
            if patfname:
                results = results.filter(patfname__icontains=patfname)

            # 姓フィールドが入力された場合のフィルタリング
            if patlname:
                results = results.filter(patlname__icontains=patlname)

            # 結果が空の場合のメッセージ表示
            if not results.exists():
                messages.error(request, '該当する患者は見つかりませんでした。')

    return render(request, 'doctor_home/patient_search.html', {'form': form, 'results': results})


def medicine_instructions(request, patient_id):
    patient = get_object_or_404(Patient, patid=patient_id)
    if request.method == 'POST':
        if 'add' in request.POST:
            form = MedicineForm(request.POST)
            if form.is_valid():
                medicine = form.cleaned_data['medicine']
                quantity = form.cleaned_data['quantity']
                # セッションに保存
                prescriptions = request.session.get('prescriptions', [])
                prescriptions.append({
                    'medicinename': medicine.medicinename,
                    'quantity': quantity,
                    'unit': medicine.unit
                })
                request.session['prescriptions'] = prescriptions
                messages.success(request, '薬剤が追加されました。')
                return redirect('medicine_instructions', patient_id=patient_id)
        elif 'delete' in request.POST:
            index = int(request.POST.get('delete'))
            prescriptions = request.session.get('prescriptions', [])
            if index < len(prescriptions):
                prescriptions.pop(index)
                request.session['prescriptions'] = prescriptions
                messages.success(request, '薬剤が削除されました。')
                return redirect('medicine_instructions', patient_id=patient_id)
    else:
        form = MedicineForm()

    context = {
        'patient': patient,
        'form': form,
        'prescriptions': request.session.get('prescriptions', [])
    }
    return render(request, 'doctor_home/medicine_instructions.html', context)

def prescription_success(request):
    return render(request, 'doctor_home/prescription_success.html')
def medicine_confirmation(request, patient_id):
    patient = get_object_or_404(Patient, patid=patient_id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            index = int(request.POST.get('delete'))
            prescriptions = request.session.get('prescriptions', [])
            if index < len(prescriptions):
                prescriptions.pop(index)
                request.session['prescriptions'] = prescriptions
                messages.success(request, '薬剤が削除されました。')
            return redirect('medicine_confirmation', patient_id=patient_id)
    prescriptions = request.session.get('prescriptions', [])
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
    }
    return render(request, 'doctor_home/medicine_confirmation.html', context)

def process_confirmed(request):
    prescriptions = request.session.get('prescriptions', [])
    if not prescriptions:
        messages.error(request, '投薬する薬剤がありません。')
        return redirect('medicine_confirmation', patient_id=request.POST.get('patient_id'))

    patient_id = request.POST.get('patient_id')

    try:
        patient = Patient.objects.get(patid=patient_id)
    except Patient.DoesNotExist:
        messages.error(request, '患者IDが見つかりません。')
        return redirect('doctor_home')

    for prescription in prescriptions:
        try:
            medicine = Medicine.objects.get(medicinename=prescription['medicinename'])
        except Medicine.DoesNotExist:
            messages.error(request, '薬剤IDが見つかりません。')
            return redirect('doctor_home')

        MedicineAdministration.objects.create(patient=patient, medicine=medicine, quantity=prescription['quantity'])
    del request.session['prescriptions']
    return redirect('prescription_success')
def treatment_history(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        return redirect('treatment_history_detail', patient_id=patient_id)
    return render(request, 'doctor_home/treatment_history.html')


def treatment_history_detail(request, patient_id):
    # 患者情報を取得
    try:
        patient = Patient.objects.get(patid=patient_id)
    except Patient.DoesNotExist:
        messages.error(request, '患者IDが見つかりません。')
        return redirect('treatment_history')

    # 処置履歴を取得
    treatments = MedicineAdministration.objects.filter(patient=patient)

    # コンテキストに患者情報と処置履歴を追加してテンプレートに渡す
    context = {
        'patient': patient,
        'treatments': treatments
    }
    return render(request, 'doctor_home/treatment_history_detail.html', context)

def doctor_medicine_instructions(request, patient_id):
    patient = get_object_or_404(Patient, patid=patient_id)
    prescriptions = request.session.get('prescriptions', [])
    form = MedicineForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        medicine = form.cleaned_data['medicine']
        quantity = form.cleaned_data['quantity']
        prescription = {
            'medicinename': medicine.medicinename,
            'quantity': quantity,
            'unit': medicine.unit
        }
        prescriptions.append(prescription)
        request.session['prescriptions'] = prescriptions
        return redirect('doctor_medicine_instructions', patient_id=patient_id)

    context = {
        'patient': patient,
        'prescriptions': prescriptions,
        'form': form,
    }
    return render(request, 'doctor_home/medicine_instructions.html', context)

def submit_prescriptions(request, patient_id):
    patient = get_object_or_404(Patient, patid=patient_id)
    prescriptions = request.session.get('prescriptions', [])

    if not prescriptions:
        messages.error(request, '追加された処方箋がありません。')
        return redirect('medicine_confirmation', patient_id=patient_id)

    for prescription in prescriptions:
        medicine = Medicine.objects.get(medicinename=prescription['medicinename'])
        MedicineAdministration.objects.create(
            patient=patient,
            medicine=medicine,
            quantity=prescription['quantity'],
            medicine_name=prescription['medicinename']
        )

    # 処方箋をセッションからクリア
    request.session['prescriptions'] = []

    # 処置完了メッセージを表示
    messages.success(request, '処置が完了しました')

    return redirect('prescription')

def prescription(request):
    return render(request, 'doctor_home/prescription_success.html')

def delete_prescription(request, patient_id, index):
    prescriptions = request.session.get('prescriptions', [])
    if 0 <= index < len(prescriptions):
        prescriptions.pop(index)
        request.session['prescriptions'] = prescriptions
    return redirect('medicine_confirmation', patient_id=patient_id)


def patient_register(request):
    if request.method == 'POST':
        patid = request.POST.get('patid')
        patfname = request.POST.get('patfname')
        patlname = request.POST.get('patlname')
        hokenmei = request.POST.get('hokenmei')
        hokenexp = request.POST.get('hokenexp')

        # エラーチェック
        errors = []
        if not patid:
            errors.append('患者IDは必須です。')
        elif not re.match(r'^[a-zA-Z0-9\u4e00-\u9faf\u3040-\u309f\u30a0-\u30ff]+$', patid):
            errors.append('患者IDには英数字、漢字、ひらがな、カタカナのみを入力してください。')
        else:
            if Patient.objects.filter(patid=patid).exists():
                errors.append('この患者IDは既に登録されています。')

        if not patfname:
            errors.append('患者名は必須です。')
        if not patlname:
            errors.append('患者姓は必須です。')
        if not hokenmei:
            errors.append('保険証記号番号は必須です。')
        elif not hokenmei.isdigit() or len(hokenmei) != 10:
            errors.append('保険証記号番号は10桁の半角数字で入力してください。')
        if not hokenexp:
            errors.append('有効期限は必須です。')
        else:
            try:
                hokenexp_date = hokenexp
                if not hokenexp_date:
                    raise ValueError
            except ValueError:
                errors.append('有効な有効期限を入力してください。')

        if errors:
            return render(request, 'uketuke_home/P101.html', {'errors': errors})

        # 確認画面表示
        if 'confirm' in request.POST:
            return render(request, 'uketuke_home/P101_confirm.html', {
                'patid': patid,
                'patfname': patfname,
                'patlname': patlname,
                'hokenmei': hokenmei,
                'hokenexp': hokenexp,
            })

        # 登録処理
        if 'register' in request.POST:
            Patient.objects.create(
                patid=patid,
                patfname=patfname,
                patlname=patlname,
                hokenmei=hokenmei,
                hokenexp=hokenexp
            )
            messages.success(request, '患者が正常に登録されました。')
            return redirect('patient_register_success')

    return render(request, 'uketuke_home/P101.html')

def patient_register_success(request):
   return render(request, 'uketuke_home/P101_success.html')


def patient_search_view(request):
    patients = None
    if request.method == 'POST':
        search_last_name = request.POST.get('search_last_name')
        search_first_name = request.POST.get('search_first_name')

        if search_last_name or search_first_name:
            patients = Patient.objects.all()

            if search_last_name:
                patients = patients.filter(patlname__icontains=search_last_name)

            if search_first_name:
                patients = patients.filter(patfname__icontains=search_first_name)

            if not patients.exists():
                messages.error(request, '該当する患者が見つかりませんでした。')
        else:
            messages.error(request, '患者姓または患者名を入力してください。')

    return render(request, 'uketuke_home/P103.html', {'patients': patients})


# 患者保険証変更


def patient_insurance_edit(request):
    if request.method == 'POST':
        mode = request.POST.get('mode')

        if mode == 'search':
            patid = request.POST.get('patid')
            try:
                patient = Patient.objects.get(patid=patid)
                return render(request, 'uketuke_home/P102.html', {'patient': patient})
            except Patient.DoesNotExist:
                messages.error(request, '患者が見つかりません。')
                return redirect('patient_insurance_edit')

        elif mode == 'modify':
            patid = request.POST.get('patid')
            patient = get_object_or_404(Patient, patid=patid)
            new_patfname = request.POST.get('patfname', patient.patfname)
            new_patlname = request.POST.get('patlname', patient.patlname)
            new_hokenmei = request.POST.get('hokenmei', patient.hokenmei)
            new_hokenexp = request.POST.get('hokenexp', patient.hokenexp)

            # 入力チェック
            errors = []
            if new_hokenmei != patient.hokenmei:
                if not new_hokenexp:
                    errors.append('保険証記号番号が変わるときは有効期限も変わっていなければなりません。')
                elif new_hokenexp <= str(patient.hokenexp):
                    errors.append(
                        '保険証記号番号が変わるときは、有効期限を現在の有効期限より新しい日付にする必要があります。')

            if new_hokenexp and new_hokenexp <= str(patient.hokenexp):
                errors.append('有効期限は現在の有効期限より新しい日付でなければなりません。')

            if not new_hokenexp:
                errors.append('有効期限が登録されていません。有効期限を入力してください。')

            if not re.match(r'^\d{10}$', new_hokenmei):
                errors.append('保険証記号番号は10桁の数字である必要があります。')

            if errors:
                return render(request, 'uketuke_home/P102.html', {
                    'patient': patient,
                    'errors': errors
                })

            if request.POST.get('action') == 'confirm':
                # 確認画面を表示
                return render(request, 'uketuke_home/confirm_patient_insurance.html', {
                    'patient': patient,
                    'new_patfname': new_patfname,
                    'new_patlname': new_patlname,
                    'new_hokenmei': new_hokenmei,
                    'new_hokenexp': new_hokenexp
                })

            elif request.POST.get('action') == 'update':
                # 保険証情報を更新
                patient.patfname = new_patfname
                patient.patlname = new_patlname
                if new_hokenmei:
                    patient.hokenmei = new_hokenmei
                if new_hokenexp:
                    patient.hokenexp = new_hokenexp
                patient.save()
                messages.success(request, '変更完了☆')
                return redirect('patient_insurance_edit')

    return render(request, 'uketuke_home/P102.html')


def patient_list(request):
   patients = Patient.objects.all()
   return render(request, 'uketuke_home/patient_list.html', {'patients': patients})


def patient_searchu(request):
    form = PatientSearchForm()
    results = None

    if request.method == 'POST':
        form = PatientSearchForm(request.POST)
        if form.is_valid():
            patlname = form.cleaned_data['patlname']
            patfname = form.cleaned_data['patfname']

            # フィルタ条件を組み合わせる
            query = Patient.objects.all()
            if patlname:
                query = query.filter(patlname__icontains=patlname)
            if patfname:
                query = query.filter(patfname__icontains=patfname)

            results = query
            if not results:
                messages.info(request, '該当する患者が見つかりませんでした。')

    return render(request, 'uketuke_home/P103.html', {
        'form': form,
        'results': results,
    })
