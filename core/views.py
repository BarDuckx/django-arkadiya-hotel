from .models import Room, Booking, Category, ExtraService
from .forms import BookingForm, CategoryForm, RoomForm, GuestDetailsForm, ExtraServiceForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
import json
from datetime import datetime, timedelta
from django.utils import timezone


def index(request):
    featured_rooms = Room.objects.filter(is_active=True)
    return render(request, 'core/index.html', {'featured_rooms': featured_rooms})


class RoomListView(ListView):
    model = Room
    template_name = 'core/room_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = Room.objects.filter(is_active=True)
        category_slug = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


@login_required(login_url='/login/')
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Для бронирования необходимо войти в систему.')
            return redirect('login')

        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        guests = request.POST.get('guests')

        if not check_in or not check_out or not guests:
            messages.error(request, 'Пожалуйста, выберите даты и количество гостей.')
            return redirect('room_detail', pk=pk)

        request.session['temp_booking'] = {
            'room_id': room.id,
            'check_in': check_in,
            'check_out': check_out,
            'guests': guests,
        }
        return redirect('checkout')

    confirmed_bookings = room.bookings.filter(
        status__in=['pending', 'confirmed'],
        check_out__gte=timezone.now().date()
    )

    occupied_dates = []
    for booking in confirmed_bookings:
        current_date = booking.check_in
        while current_date < booking.check_out:
            occupied_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

    context = {
        'room': room,
        'occupied_dates': json.dumps(occupied_dates),
        'form': BookingForm()
    }
    return render(request, 'core/room_detail.html', context)


@login_required
def checkout(request):
    temp_data = request.session.get('temp_booking')
    if not temp_data:
        return redirect('room_list')

    room = get_object_or_404(Room, id=temp_data['room_id'])
    services = ExtraService.objects.filter(is_active=True)

    check_in = datetime.strptime(temp_data['check_in'], '%Y-%m-%d').date()
    check_out = datetime.strptime(temp_data['check_out'], '%Y-%m-%d').date()
    nights = (check_out - check_in).days
    guests = int(temp_data['guests'])
    total_price = room.price_per_night * nights * int(temp_data['guests'])

    form = GuestDetailsForm()

    return render(request, 'core/checkout.html', {
        'room': room,
        'form': form,
        'services': services,
        'check_in': check_in,
        'check_out': check_out,
        'nights': nights,
        'guests': guests,
        'total_price': total_price,
    })


@login_required
def process_checkout(request):
    if request.method == 'POST':
        form = GuestDetailsForm(request.POST)
        temp_data = request.session.get('temp_booking')

        if form.is_valid() and temp_data:
            room = get_object_or_404(Room, id=temp_data['room_id'])

            try:
                check_in_date = datetime.strptime(temp_data['check_in'], '%Y-%m-%d').date()
                check_out_date = datetime.strptime(temp_data['check_out'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                messages.error(request, "Ошибка формата дат.")
                return redirect('room_detail', pk=room.id)

            booking = Booking.objects.create(
                user=request.user,
                room=room,
                check_in=check_in_date,
                check_out=check_out_date,
                guests=int(temp_data['guests']),
                full_name=form.cleaned_data['full_name'],
                passport=form.cleaned_data['passport'],
                phone=form.cleaned_data['phone'],
                email_guest=form.cleaned_data.get('email', ''),
                total_price=room.price_per_night * (check_out_date - check_in_date).days * int(temp_data['guests'])
            )

            service_ids = request.POST.getlist('services')
            if service_ids:
                from .models import ExtraService
                selected_services = ExtraService.objects.filter(id__in=service_ids)
                booking.extra_services.set(selected_services)

                services_cost = sum(s.price for s in selected_services)
                booking.total_price += services_cost
                booking.save()

            del request.session['temp_booking']
            messages.success(request, 'Заявка на бронирование успешно оформлена!')
            return redirect('profile')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return redirect('checkout')


@login_required
def user_profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/profile.html', {'bookings': bookings})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == 'pending':
        booking.status = 'canceled'
        booking.save()
        messages.info(request, "Бронирование отменено.")
    return redirect('profile')


@staff_member_required
def custom_admin_dashboard(request):
    if request.method == 'POST' and 'change_status' in request.POST:
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('new_status')
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = new_status
        booking.save()
        messages.success(request, f"Статус брони #{booking.id} изменен на {booking.get_status_display()}")
        return redirect('custom_admin')

    bookings = Booking.objects.all().order_by('-created_at')
    rooms = Room.objects.all()
    categories = Category.objects.all()
    users = User.objects.all()
    services = ExtraService.objects.all()

    total_bookings = bookings.count()
    active_bookings = bookings.filter(status__in=['pending', 'confirmed']).count()
    total_users = users.count()

    return render(request, 'core/admin_dashboard.html', {
        'bookings': bookings,
        'rooms': rooms,
        'categories': categories,
        'users': users,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_users': total_users,
        'services': services,
    })

@staff_member_required
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk) if pk else None
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория сохранена!")
            return redirect('custom_admin')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'core/admin_form.html', {'form': form, 'title': 'Категория'})

@staff_member_required
def category_delete(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=pk)
        category.delete()
        messages.success(request, f'Категория {category.name} удалена.')
    return redirect('/dashboard/?tab=categories')

@staff_member_required
def edit_room(request, pk=None):
    room = get_object_or_404(Room, pk=pk) if pk else None
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)

        if form.is_valid():
            form.save()
            messages.success(request, "Номер сохранен!")
            return redirect('custom_admin')
    else:
        form = RoomForm(instance=room)
    return render(request, 'core/admin_form.html', {'form': form, 'title': 'Номер'})

@staff_member_required
def room_delete(request, pk):
    if request.method == 'POST':
        room = get_object_or_404(Room, id=pk)
        room.delete()
        messages.success(request, f'Номер {room.number} успешно удален.')
    return redirect('/dashboard/?tab=rooms')

@staff_member_required
def edit_service(request, pk=None):
    service = get_object_or_404(ExtraService, pk=pk) if pk else None
    if request.method == 'POST':
        form = ExtraServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Услуга успешно сохранена!")
            return redirect('/dashboard/?tab=services')
    else:
        form = ExtraServiceForm(instance=service)
    return render(request, 'core/admin_form.html', {'form': form, 'title': 'Дополнительная услуга'})

@staff_member_required
def service_delete(request, pk):
    if request.method == 'POST':
        service = get_object_or_404(ExtraService, id=pk)
        service.delete()
        messages.success(request, "Услуга удалена.")
    return redirect('/dashboard/?tab=services')
