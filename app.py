import pymysql
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import pygame
import random
import os
from datetime import datetime, timedelta
import hashlib
from decimal import Decimal
# ===============================================
# Класс для пазл-капчи
# ===============================================

class PuzzleCaptcha:
    def __init__(self):
        self.success = False
        self.attempts = 0
        self.max_attempts = 3
        
    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((400, 500))
        pygame.display.set_caption("Пазл-капча")
        
        SIZE = 200
        images = []
        
        # Загружаем изображения
        image_files = [f for f in os.listdir() if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        for file in image_files[:4]:
            try:
                img = pygame.transform.scale(pygame.image.load(file), (SIZE, SIZE))
                images.append(img)
            except:
                print(f"Не удалось загрузить изображение: {file}")
        
        # Создаем недостающие изображения
        for i in range(4 - len(images)):
            surf = pygame.Surface((SIZE, SIZE))
            surf.fill([(255,0,0), (0,255,0), (0,0,255), (255,255,0)][i])
            images.append(surf)
        
        order = list(range(4))
        random.shuffle(order)
        dragging = None
        positions = [(0,0), (SIZE,0), (0,SIZE), (SIZE,SIZE)]
        
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # Создаем кнопку
        button_rect = pygame.Rect(150, 420, 100, 40)
        button_color = (70, 130, 180)
        button_hover_color = (100, 160, 210)
        button_text = "Проверить"
        
        running = True
        clock = pygame.time.Clock()
        mouse_pos = (0, 0)
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            button_hover = button_rect.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    running = False
                    self.success = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Проверка клика по кнопке
                    if button_rect.collidepoint(event.pos):
                        if order == list(range(4)):
                            self.success = True
                            running = False
                        else:
                            self.attempts += 1
                            if self.attempts >= self.max_attempts:
                                running = False
                                self.success = False
                            else:
                                # Перемешиваем пазл при неудачной попытке
                                random.shuffle(order)
                    
                    # Проверка клика по пазлу
                    x, y = event.pos
                    if y < 400:
                        for i, (px, py) in enumerate(positions):
                            if px <= x < px + SIZE and py <= y < py + SIZE:
                                dragging = i
                                break
                
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging is not None:
                    x, y = event.pos
                    if y < 400:
                        for i, (px, py) in enumerate(positions):
                            if px <= x < px + SIZE and py <= y < py + SIZE and i != dragging:
                                order[dragging], order[i] = order[i], order[dragging]
                                break
                    dragging = None
            
            screen.fill((255, 255, 255))
            
            # Рисуем все элементы, кроме перетаскиваемого
            for i in range(4):
                if i != dragging:
                    screen.blit(images[order[i]], positions[i])
            
            # Рисуем перетаскиваемый элемент последним
            if dragging is not None:
                centered_pos = (mouse_pos[0] - SIZE // 2, mouse_pos[1] - SIZE // 2)
                screen.blit(images[order[dragging]], centered_pos)
            
            # Рисуем кнопку
            current_button_color = button_hover_color if button_hover else button_color
            pygame.draw.rect(screen, current_button_color, button_rect, border_radius=8)
            pygame.draw.rect(screen, (50, 50, 50), button_rect, 2, border_radius=8)
            
            button_surface = small_font.render(button_text, True, (255, 255, 255))
            button_text_rect = button_surface.get_rect(center=button_rect.center)
            screen.blit(button_surface, button_text_rect)
            
            # Отображаем только количество попыток
            attempts_text = small_font.render(f"Попытки: {self.attempts}/{self.max_attempts}", True, (0, 0, 0))
            screen.blit(attempts_text, (10, 470))
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        return self.success

# ===============================================
# Класс для работы с базой данных
# ===============================================

class Database:
    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host='localhost',
                user='root',
                password='root',
                database='internet__provider02',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print("✓ Успешное подключение к базе данных")
        except pymysql.err.OperationalError as e:
            messagebox.showerror("Ошибка базы данных", 
                               f"Не удалось подключиться к базе данных.\nОшибка: {e}\n\n"
                               "Проверьте:\n"
                               "1. Запущен ли MySQL сервер\n"
                               "2. Правильность логина/пароля\n"
                               "3. Существует ли база данных 'internet__provider'\n\n"
                               "Запустите create_database_complete.sql для создания базы.")
            print(f"Ошибка подключения: {e}")
            raise e
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {e}")
            raise e
    
    def close(self):
        """Закрывает соединение с базой данных"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            print("✗ Соединение с базой данных закрыто")
    
    def check_connection(self):
        """Проверяет соединение с базой данных"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except:
            return False
    
    # ===============================================
    # АУТЕНТИФИКАЦИЯ И ПОЛЬЗОВАТЕЛИ
    # ===============================================
    
    def auth(self, username, password):
        """Аутентификация пользователя"""
        try:
            with self.connection.cursor() as cursor:
                # Хешируем пароль для проверки
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Получаем текущие данные пользователя
                cursor.execute("SELECT id, username, password, role, is_active, failed_attempts FROM users WHERE username=%s", (username,))
                result = cursor.fetchone()
                
                if not result:
                    return None
                
                user_data = result
                
                # Проверяем заблокирован ли пользователь
                if not user_data['is_active']:
                    return "blocked"
                
                # Проверяем пароль
                if password_hash == user_data['password']:
                    # Сбрасываем счетчик неудачных попыток при успешной авторизации
                    cursor.execute("UPDATE users SET failed_attempts=0, last_login=NOW() WHERE id=%s", (user_data['id'],))
                    
                    # Получаем ID клиента если это клиент
                    client_id = None
                    if user_data['role'] == 'client':
                        cursor.execute("SELECT ClientID FROM Clients WHERE UserID=%s", (user_data['id'],))
                        client_data = cursor.fetchone()
                        if client_data:
                            client_id = client_data['ClientID']
                    
                    self.connection.commit()
                    return {
                        'id': user_data['id'],
                        'username': user_data['username'], 
                        'role': user_data['role'],
                        'client_id': client_id
                    }
                else:
                    # Увеличиваем счетчик неудачных попыток для ЭТОГО пользователя
                    new_attempts = user_data['failed_attempts'] + 1
                    cursor.execute("UPDATE users SET failed_attempts=%s WHERE id=%s", 
                                 (new_attempts, user_data['id']))
                    
                    # Блокируем если 3 неудачные попытки у ЭТОГО пользователя
                    if new_attempts >= 3:
                        cursor.execute("UPDATE users SET is_active=0 WHERE id=%s", (user_data['id'],))
                        self.connection.commit()
                        return "blocked"
                    
                    self.connection.commit()
                    return None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных при аутентификации: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Получает пользователя по ID"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка получения пользователя: {e}")
            return None
    
    # ===============================================
    # ПОЛЬЗОВАТЕЛИ (ДЛЯ АДМИНИСТРАТОРА)
    # ===============================================
    
    def get_users(self):
        """Получает всех пользователей"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        u.id, u.username, u.role, u.is_active, u.failed_attempts, 
                        u.last_login, u.created_at, u.updated_at,
                        c.ClientID as client_id,
                        CASE 
                            WHEN c.ClientID IS NOT NULL THEN 'Да' 
                            ELSE 'Нет' 
                        END as has_client
                    FROM users u
                    LEFT JOIN Clients c ON u.id = c.UserID
                    ORDER BY u.created_at DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка получения пользователей: {e}")
            return []
    
    def delete_user(self, user_id):
        """Удаляет пользователя и связанные данные"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем, есть ли связанный клиент
                cursor.execute("SELECT ClientID FROM Clients WHERE UserID=%s", (user_id,))
                client = cursor.fetchone()
                
                if client:
                    # Удаляем связанного клиента
                    client_id = client['ClientID']
                    
                    # Удаляем связанные данные клиента (в правильном порядке для избежания ошибок внешних ключей)
                    cursor.execute("DELETE FROM BalanceHistory WHERE ClientID=%s", (client_id,))
                    cursor.execute("DELETE FROM Notifications WHERE ClientID=%s", (client_id,))
                    cursor.execute("DELETE FROM ClientServices WHERE ConnectionID IN (SELECT ConnectionID FROM Connections WHERE ClientID=%s)", (client_id,))
                    cursor.execute("DELETE FROM Payments WHERE ClientID=%s", (client_id,))
                    cursor.execute("DELETE FROM Equipment WHERE ClientID=%s", (client_id,))
                    cursor.execute("DELETE FROM Connections WHERE ClientID=%s", (client_id,))
                    cursor.execute("DELETE FROM Clients WHERE ClientID=%s", (client_id,))
                
                # Удаляем пользователя
                cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
                
                self.connection.commit()
                return True, "Пользователь и связанные данные успешно удалены"
        except Exception as e:
            return False, f"Ошибка удаления пользователя: {e}"
    
    def delete_user_with_confirmation(self, user_id, username):
        """Удаляет пользователя с подтверждением и отображением связанных данных"""
        try:
            with self.connection.cursor() as cursor:
                # Получаем информацию о связанных данных
                related_data = []
                
                # Проверяем, есть ли связанный клиент
                cursor.execute("SELECT ClientID FROM Clients WHERE UserID=%s", (user_id,))
                client = cursor.fetchone()
                
                if client:
                    client_id = client['ClientID']
                    related_data.append(f"Клиент (ID: {client_id})")
                    
                    # Получаем количество связанных записей
                    cursor.execute("SELECT COUNT(*) as count FROM Connections WHERE ClientID=%s", (client_id,))
                    connections = cursor.fetchone()
                    if connections['count'] > 0:
                        related_data.append(f"Подключения ({connections['count']} записей)")
                    
                    cursor.execute("SELECT COUNT(*) as count FROM Payments WHERE ClientID=%s", (client_id,))
                    payments = cursor.fetchone()
                    if payments['count'] > 0:
                        related_data.append(f"Платежи ({payments['count']} записей)")
                    
                    cursor.execute("SELECT COUNT(*) as count FROM Notifications WHERE ClientID=%s", (client_id,))
                    notifications = cursor.fetchone()
                    if notifications['count'] > 0:
                        related_data.append(f"Уведомления ({notifications['count']} записей)")
                
                return related_data
        except Exception as e:
            print(f"Ошибка получения информации о связанных данных: {e}")
            return []
    
    # ===============================================
    # КЛИЕНТЫ
    # ===============================================
    
    def get_clients(self):
        """Получает всех клиентов"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        c.ClientID, c.UserID, c.Username, 
                        c.FirstName, c.LastName, c.MiddleName,
                        c.DateOfBirth, c.PassportSeries, c.PassportNumber,
                        c.IssueDate, c.IssuedBy, c.RegistrationAddress,
                        c.ActualAddress, c.PhoneNumber, c.Email,
                        c.IsActive, c.Balance, c.PersonalDiscount,
                        c.CreationDate,
                        (SELECT COUNT(*) FROM Connections WHERE ClientID = c.ClientID AND Status='Active') as ActiveConnections,
                        (SELECT SUM(Amount) FROM Payments WHERE ClientID = c.ClientID AND Status='Completed') as TotalPayments
                    FROM Clients c
                    ORDER BY c.CreationDate DESC
                """)
                clients = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for client in clients:
                    if 'Balance' in client and client['Balance'] is not None:
                        client['Balance'] = float(client['Balance'])
                    if 'PersonalDiscount' in client and client['PersonalDiscount'] is not None:
                        client['PersonalDiscount'] = float(client['PersonalDiscount'])
                    if 'TotalPayments' in client and client['TotalPayments'] is not None:
                        client['TotalPayments'] = float(client['TotalPayments'])
                
                return clients
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка получения клиентов: {e}")
            return []
    
    def get_client_by_id(self, client_id):
        """Получает клиента по ID"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Clients WHERE ClientID=%s", (client_id,))
                client = cursor.fetchone()
                
                if client and 'Balance' in client and client['Balance'] is not None:
                    client['Balance'] = float(client['Balance'])
                if client and 'PersonalDiscount' in client and client['PersonalDiscount'] is not None:
                    client['PersonalDiscount'] = float(client['PersonalDiscount'])
                
                return client
        except Exception as e:
            print(f"Ошибка получения клиента: {e}")
            return None
    
    def get_client_by_username(self, username):
        """Получает клиента по имени пользователя"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        c.*,
                        u.id as UserID
                    FROM Clients c
                    JOIN users u ON c.UserID = u.id
                    WHERE u.username=%s
                """, (username,))
                client = cursor.fetchone()
                
                if client:
                    if 'Balance' in client and client['Balance'] is not None:
                        client['Balance'] = float(client['Balance'])
                    if 'PersonalDiscount' in client and client['PersonalDiscount'] is not None:
                        client['PersonalDiscount'] = float(client['PersonalDiscount'])
                
                return client
        except Exception as e:
            print(f"Ошибка получения клиента: {e}")
            return None
    
    def get_client_by_user_id(self, user_id):
        """Получает клиента по UserID"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Clients WHERE UserID=%s", (user_id,))
                client = cursor.fetchone()
                
                if client and 'Balance' in client and client['Balance'] is not None:
                    client['Balance'] = float(client['Balance'])
                if client and 'PersonalDiscount' in client and client['PersonalDiscount'] is not None:
                    client['PersonalDiscount'] = float(client['PersonalDiscount'])
                
                return client
        except Exception as e:
            print(f"Ошибка получения клиента: {e}")
            return None
    
    def add_client(self, client_data):
        """Добавляет нового клиента"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем уникальность логина
                cursor.execute("SELECT ClientID FROM Clients WHERE Username=%s", (client_data['username'],))
                if cursor.fetchone():
                    return False, "Клиент с указанным логином уже существует"
                
                # Проверяем уникальность телефона
                cursor.execute("SELECT ClientID FROM Clients WHERE PhoneNumber=%s", (client_data['phone'],))
                if cursor.fetchone():
                    return False, "Клиент с указанным номером телефона уже существует"
                
                # Создаем пользователя
                password_hash = hashlib.sha256(client_data['password'].encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (username, password, role, is_active) 
                    VALUES (%s, %s, 'client', 1)
                """, (client_data['username'], password_hash))
                
                user_id = cursor.lastrowid
                
                # Создаем клиента
                query = """
                    INSERT INTO Clients (
                        UserID, Username, PasswordHash, FirstName, LastName, MiddleName,
                        DateOfBirth, PassportSeries, PassportNumber, IssueDate, IssuedBy,
                        RegistrationAddress, ActualAddress, PhoneNumber, Email, IsActive, Balance
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """
                
                cursor.execute(query, (
                    user_id,
                    client_data['username'],
                    password_hash,
                    client_data['first_name'],
                    client_data['last_name'],
                    client_data.get('middle_name', ''),
                    client_data.get('birth_date'),
                    client_data['passport_series'],
                    client_data['passport_number'],
                    client_data.get('issue_date'),
                    client_data.get('issued_by', ''),
                    client_data['reg_address'],
                    client_data.get('actual_address', ''),
                    client_data['phone'],
                    client_data.get('email', ''),
                    True
                ))
                
                client_id = cursor.lastrowid
                
                # Создаем подключение с первым доступным тарифом
                cursor.execute("SELECT TariffID FROM TariffPlans WHERE IsActive=1 LIMIT 1")
                tariff = cursor.fetchone()
                
                if tariff:
                    cursor.execute("SELECT MonthlyCost FROM TariffPlans WHERE TariffID=%s", (tariff['TariffID'],))
                    tariff_cost = cursor.fetchone()
                    
                    cursor.execute("""
                        INSERT INTO Connections (ClientID, TariffID, ConnectionDate, Status, MonthlyPayment, NextPaymentDate)
                        VALUES (%s, %s, CURDATE(), 'Active', %s, DATE_ADD(CURDATE(), INTERVAL 1 MONTH))
                    """, (client_id, tariff['TariffID'], tariff_cost['MonthlyCost']))
                
                # Создаем приветственное уведомление
                cursor.execute("""
                    INSERT INTO Notifications (ClientID, Title, Message, Type)
                    VALUES (%s, 'Добро пожаловать!', 'Спасибо за регистрацию в нашей системе! Ваш аккаунт успешно создан.', 'Promotion')
                """, (client_id,))
                
                self.connection.commit()
                return True, client_id
        except Exception as e:
            return False, f"Ошибка добавления клиента: {e}"
    
    def update_client(self, client_id, client_data):
        """Обновляет данные клиента"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем уникальность логина
                cursor.execute("SELECT ClientID FROM Clients WHERE Username=%s AND ClientID!=%s", 
                             (client_data['username'], client_id))
                if cursor.fetchone():
                    return False, "Клиент с указанным логином уже существует"
                
                # Проверяем уникальность телефона
                cursor.execute("SELECT ClientID FROM Clients WHERE PhoneNumber=%s AND ClientID!=%s", 
                             (client_data['phone'], client_id))
                if cursor.fetchone():
                    return False, "Клиент с указанным номером телефона уже существует"
                
                # Получаем UserID клиента
                cursor.execute("SELECT UserID FROM Clients WHERE ClientID=%s", (client_id,))
                user_result = cursor.fetchone()
                user_id = user_result['UserID'] if user_result else None
                
                # Обновляем пользователя
                if user_id:
                    cursor.execute("UPDATE users SET username=%s WHERE id=%s", 
                                 (client_data['username'], user_id))
                
                # Обновляем клиента
                query = """
                    UPDATE Clients SET 
                        Username=%s, FirstName=%s, LastName=%s, MiddleName=%s,
                        DateOfBirth=%s, PhoneNumber=%s, Email=%s, 
                        ActualAddress=%s, IsActive=%s
                    WHERE ClientID=%s
                """
                
                cursor.execute(query, (
                    client_data['username'],
                    client_data['first_name'],
                    client_data['last_name'],
                    client_data.get('middle_name', ''),
                    client_data.get('birth_date'),
                    client_data['phone'],
                    client_data.get('email', ''),
                    client_data.get('actual_address', ''),
                    client_data['is_active'],
                    client_id
                ))
                
                self.connection.commit()
                return True, "Данные клиента обновлены"
        except Exception as e:
            return False, f"Ошибка обновления клиента: {e}"
    
    def delete_client(self, client_id):
        """Удаляет клиента и связанного пользователя"""
        try:
            with self.connection.cursor() as cursor:
                # Получаем UserID клиента
                cursor.execute("SELECT UserID FROM Clients WHERE ClientID=%s", (client_id,))
                user_result = cursor.fetchone()
                user_id = user_result['UserID'] if user_result else None
                
                # Удаляем связанные данные клиента (в правильном порядке для избежания ошибок внешних ключей)
                cursor.execute("DELETE FROM BalanceHistory WHERE ClientID=%s", (client_id,))
                cursor.execute("DELETE FROM Notifications WHERE ClientID=%s", (client_id,))
                cursor.execute("DELETE FROM ClientServices WHERE ConnectionID IN (SELECT ConnectionID FROM Connections WHERE ClientID=%s)", (client_id,))
                cursor.execute("DELETE FROM Payments WHERE ClientID=%s", (client_id,))
                cursor.execute("DELETE FROM Equipment WHERE ClientID=%s", (client_id,))
                cursor.execute("DELETE FROM Connections WHERE ClientID=%s", (client_id,))
                cursor.execute("DELETE FROM Clients WHERE ClientID=%s", (client_id,))
                
                # Удаляем пользователя
                if user_id:
                    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
                
                self.connection.commit()
                return True, "Клиент и связанный пользователь удалены"
        except Exception as e:
            return False, f"Ошибка удаления клиента: {e}"
    
    def get_client_dashboard_info(self, client_id):
        """Получает информацию для дашборда клиента"""
        try:
            with self.connection.cursor() as cursor:
                # Получаем информацию о клиенте
                cursor.execute("SELECT * FROM Clients WHERE ClientID=%s", (client_id,))
                client_info = cursor.fetchone()
                
                # Получаем активное подключение
                cursor.execute("""
                    SELECT 
                        c.*,
                        t.TariffName,
                        t.DownloadSpeedMbps,
                        t.UploadSpeedMbps
                    FROM Connections c
                    JOIN TariffPlans t ON c.TariffID = t.TariffID
                    WHERE c.ClientID=%s AND c.Status='Active'
                    ORDER BY c.ConnectionDate DESC
                    LIMIT 1
                """, (client_id,))
                connection_info = cursor.fetchone()
                
                # Конвертируем Decimal в float
                if client_info and 'Balance' in client_info and client_info['Balance'] is not None:
                    client_info['Balance'] = float(client_info['Balance'])
                
                if connection_info and 'MonthlyPayment' in connection_info and connection_info['MonthlyPayment'] is not None:
                    connection_info['MonthlyPayment'] = float(connection_info['MonthlyPayment'])
                
                return {
                    'client': client_info,
                    'connection': connection_info
                }
        except Exception as e:
            print(f"Ошибка получения информации для дашборда: {e}")
            return None
    
    # ===============================================
    # ТАРИФЫ
    # ===============================================
    
    def get_tariffs(self):
        """Получает все тарифы"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        TariffID, TariffName, DownloadSpeedMbps, UploadSpeedMbps, 
                        MonthlyCost, Description, IsActive, CreatedAt, UpdatedAt,
                        (SELECT COUNT(*) FROM Connections WHERE TariffID = t.TariffID AND Status='Active') as ActiveConnections
                    FROM TariffPlans t
                    ORDER BY MonthlyCost
                """)
                tariffs = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for tariff in tariffs:
                    if 'MonthlyCost' in tariff and tariff['MonthlyCost'] is not None:
                        tariff['MonthlyCost'] = float(tariff['MonthlyCost'])
                
                return tariffs
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка получения тарифов: {e}")
            return []
    
    def add_tariff(self, tariff_data):
        """Добавляет новый тариф"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO TariffPlans (TariffName, DownloadSpeedMbps, UploadSpeedMbps, MonthlyCost, Description, IsActive)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    tariff_data['name'],
                    tariff_data['download_speed'],
                    tariff_data['upload_speed'],
                    tariff_data['monthly_cost'],
                    tariff_data.get('description', ''),
                    True
                ))
                
                self.connection.commit()
                return True, "Тариф успешно добавлен"
        except Exception as e:
            return False, f"Ошибка добавления тарифа: {e}"
    
    def update_tariff(self, tariff_id, tariff_data):
        """Обновляет данные тарифа"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE TariffPlans SET 
                        TariffName=%s, DownloadSpeedMbps=%s, UploadSpeedMbps=%s, 
                        MonthlyCost=%s, Description=%s, IsActive=%s, UpdatedAt=NOW()
                    WHERE TariffID=%s
                """, (
                    tariff_data['name'],
                    tariff_data['download_speed'],
                    tariff_data['upload_speed'],
                    tariff_data['monthly_cost'],
                    tariff_data.get('description', ''),
                    tariff_data['is_active'],
                    tariff_id
                ))
                
                self.connection.commit()
                return True, "Данные тарифа обновлены"
        except Exception as e:
            return False, f"Ошибка обновления тарифа: {e}"
    
    def delete_tariff(self, tariff_id):
        """Удаляет тариф"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем, есть ли активные подключения с этим тарифом
                cursor.execute("SELECT COUNT(*) as count FROM Connections WHERE TariffID=%s AND Status='Active'", (tariff_id,))
                result = cursor.fetchone()
                
                if result['count'] > 0:
                    return False, "Невозможно удалить тариф, так как существуют активные подключения"
                
                cursor.execute("DELETE FROM TariffPlans WHERE TariffID=%s", (tariff_id,))
                self.connection.commit()
                return True, "Тариф удален"
        except Exception as e:
            return False, f"Ошибка удаления тарифа: {e}"
    
    # ===============================================
    # УСЛУГИ
    # ===============================================
    
    def get_services(self):
        """Получает все услуги"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ServiceID, ServiceName, MonthlyCost, Description, 
                        IsActive, CreatedAt, UpdatedAt,
                        (SELECT COUNT(*) FROM ClientServices WHERE ServiceID = s.ServiceID AND IsActive=1) as ActiveConnections
                    FROM Services s
                    ORDER BY ServiceName
                """)
                services = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for service in services:
                    if 'MonthlyCost' in service and service['MonthlyCost'] is not None:
                        service['MonthlyCost'] = float(service['MonthlyCost'])
                
                return services
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка получения услуг: {e}")
            return []
    
    def add_service(self, service_data):
        """Добавляет новую услугу"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Services (ServiceName, MonthlyCost, Description, IsActive)
                    VALUES (%s, %s, %s, %s)
                """, (
                    service_data['name'],
                    service_data['monthly_cost'],
                    service_data.get('description', ''),
                    True
                ))
                
                self.connection.commit()
                return True, "Услуга успешно добавлена"
        except Exception as e:
            return False, f"Ошибка добавления услуги: {e}"
    
    def update_service(self, service_id, service_data):
        """Обновляет данные услуги"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Services SET 
                        ServiceName=%s, MonthlyCost=%s, Description=%s, 
                        IsActive=%s, UpdatedAt=NOW()
                    WHERE ServiceID=%s
                """, (
                    service_data['name'],
                    service_data['monthly_cost'],
                    service_data.get('description', ''),
                    service_data['is_active'],
                    service_id
                ))
                
                self.connection.commit()
                return True, "Данные услуги обновлены"
        except Exception as e:
            return False, f"Ошибка обновления услуги: {e}"
    
    def delete_service(self, service_id):
        """Удаляет услугу"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем, есть ли активные подключения с этой услугой
                cursor.execute("""
                    SELECT COUNT(*) as count FROM ClientServices cs
                    WHERE cs.ServiceID=%s AND cs.IsActive=1
                """, (service_id,))
                result = cursor.fetchone()
                
                if result['count'] > 0:
                    return False, "Невозможно удалить услугу, так как существуют активные подключения"
                
                cursor.execute("DELETE FROM Services WHERE ServiceID=%s", (service_id,))
                self.connection.commit()
                return True, "Услуга удалена"
        except Exception as e:
            return False, f"Ошибка удаления услуги: {e}"
    
    # ===============================================
    # ПОДКЛЮЧЕНИЯ
    # ===============================================
    
    def get_connections(self, client_id=None):
        """Получает подключения (все или для конкретного клиента)"""
        try:
            with self.connection.cursor() as cursor:
                query = """
                    SELECT 
                        c.ConnectionID, c.ClientID, c.TariffID, c.ConnectionDate,
                        c.Status, c.MonthlyPayment, c.NextPaymentDate, 
                        c.TerminationDate, c.TerminationReason,
                        cl.FirstName, cl.LastName,
                        t.TariffName, t.DownloadSpeedMbps, t.UploadSpeedMbps
                    FROM Connections c
                    JOIN Clients cl ON c.ClientID = cl.ClientID
                    JOIN TariffPlans t ON c.TariffID = t.TariffID
                """
                
                if client_id:
                    query += " WHERE c.ClientID=%s"
                    cursor.execute(query, (client_id,))
                else:
                    query += " ORDER BY c.ConnectionDate DESC"
                    cursor.execute(query)
                
                connections = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for conn in connections:
                    if 'MonthlyPayment' in conn and conn['MonthlyPayment'] is not None:
                        conn['MonthlyPayment'] = float(conn['MonthlyPayment'])
                
                return connections
        except Exception as e:
            print(f"Ошибка получения подключений: {e}")
            return []
    
    def create_connection(self, client_id, tariff_id, connection_date=None):
        """Создает новое подключение"""
        try:
            with self.connection.cursor() as cursor:
                if not connection_date:
                    connection_date = datetime.now().date()
                
                # Получаем стоимость тарифа
                cursor.execute("SELECT MonthlyCost FROM TariffPlans WHERE TariffID=%s", (tariff_id,))
                tariff_cost = cursor.fetchone()
                
                if not tariff_cost:
                    return False, "Тариф не найден"
                
                monthly_payment = tariff_cost['MonthlyCost']
                next_payment_date = (connection_date + timedelta(days=30)).strftime('%Y-%m-%d')
                
                cursor.execute("""
                    INSERT INTO Connections (ClientID, TariffID, ConnectionDate, Status, MonthlyPayment, NextPaymentDate)
                    VALUES (%s, %s, %s, 'Active', %s, %s)
                """, (client_id, tariff_id, connection_date, monthly_payment, next_payment_date))
                
                connection_id = cursor.lastrowid
                
                # Создаем уведомление
                cursor.execute("""
                    INSERT INTO Notifications (ClientID, Title, Message, Type)
                    VALUES (%s, 'Новое подключение', 'Создано новое интернет-подключение.', 'Service')
                """, (client_id,))
                
                self.connection.commit()
                return True, connection_id
        except Exception as e:
            return False, f"Ошибка создания подключения: {e}"
    
    def update_connection_status(self, connection_id, status, termination_reason=None):
        """Обновляет статус подключения"""
        try:
            with self.connection.cursor() as cursor:
                update_data = {
                    'Status': status,
                    'UpdatedAt': 'NOW()'
                }
                
                if status == 'Terminated':
                    update_data['TerminationDate'] = 'CURDATE()'
                    if termination_reason:
                        update_data['TerminationReason'] = termination_reason
                
                set_clause = ', '.join([f"{k}={v}" if isinstance(v, str) and v.startswith('NOW') or v.startswith('CURDATE') else f"{k}=%s" for k, v in update_data.items()])
                values = [v for v in update_data.values() if not (isinstance(v, str) and (v.startswith('NOW') or v.startswith('CURDATE')))]
                values.append(connection_id)
                
                cursor.execute(f"UPDATE Connections SET {set_clause} WHERE ConnectionID=%s", tuple(values))
                
                self.connection.commit()
                return True, f"Статус подключения изменен на '{status}'"
        except Exception as e:
            return False, f"Ошибка обновления статуса подключения: {e}"
    
    # ===============================================
    # ПЛАТЕЖИ (ОБНОВЛЕННЫЕ МЕТОДЫ)
    # ===============================================
    
    def get_payments(self, client_id=None, start_date=None, end_date=None, status=None):
        """Получает платежи с фильтрацией"""
        try:
            with self.connection.cursor() as cursor:
                query = """
                    SELECT 
                        p.PaymentID, p.ClientID, p.Amount, p.PaymentDate,
                        p.PaymentMethod, p.PaymentPeriod, p.Status,
                        p.Description, p.TransactionID, p.ReceiptNumber,
                        p.CreatedAt, p.UpdatedAt,
                        CONCAT(c.LastName, ' ', LEFT(c.FirstName, 1), '.') as ClientName
                    FROM Payments p
                    LEFT JOIN Clients c ON p.ClientID = c.ClientID
                    WHERE 1=1
                """
                params = []
                
                if client_id:
                    query += " AND p.ClientID=%s"
                    params.append(client_id)
                
                if start_date:
                    query += " AND DATE(p.PaymentDate) >= %s"
                    params.append(start_date)
                
                if end_date:
                    query += " AND DATE(p.PaymentDate) <= %s"
                    params.append(end_date)
                
                if status:
                    query += " AND p.Status=%s"
                    params.append(status)
                
                query += " ORDER BY p.PaymentDate DESC LIMIT 1000"
                
                cursor.execute(query, tuple(params))
                payments = cursor.fetchall()
                
                # Конвертируем Decimal в float и даты
                for payment in payments:
                    if 'Amount' in payment and payment['Amount'] is not None:
                        payment['Amount'] = float(payment['Amount'])
                    if payment.get('PaymentPeriod'):
                        # Исправление: проверяем, является ли PaymentPeriod строкой или datetime
                        if hasattr(payment['PaymentPeriod'], 'strftime'):
                            payment['PaymentPeriod'] = payment['PaymentPeriod'].strftime('%Y-%m')
                        else:
                            # Если это строка, оставляем как есть
                            payment['PaymentPeriod'] = str(payment['PaymentPeriod'])
                
                return payments
        except Exception as e:
            print(f"Ошибка получения платежей: {e}")
            return []
    
    def get_client_payments(self, client_id, period='all'):
        """Получает платежи клиента (обратная совместимость)"""
        end_date = datetime.now()
        start_date = None
        
        if period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == '3months':
            start_date = end_date - timedelta(days=90)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        
        return self.get_payments(client_id=client_id, start_date=start_date, end_date=end_date)
    
    def get_client_payments_filtered(self, client_id, start_date=None, end_date=None):
        """Получает платежи клиента с фильтрацией по датам"""
        return self.get_payments(client_id=client_id, start_date=start_date, end_date=end_date)
    
    def get_payment_statistics(self, client_id=None):
        """Получает статистику по платежам"""
        try:
            with self.connection.cursor() as cursor:
                if client_id:
                    query = """
                        SELECT 
                            COUNT(*) as total_payments,
                            SUM(Amount) as total_amount,
                            AVG(Amount) as average_payment,
                            MIN(PaymentDate) as first_payment,
                            MAX(PaymentDate) as last_payment,
                            SUM(CASE WHEN Status='Completed' THEN Amount ELSE 0 END) as completed_amount,
                            SUM(CASE WHEN Status='Pending' THEN Amount ELSE 0 END) as pending_amount,
                            SUM(CASE WHEN Status='Failed' THEN Amount ELSE 0 END) as failed_amount,
                            COUNT(CASE WHEN Status='Completed' THEN 1 END) as completed_count,
                            COUNT(CASE WHEN Status='Pending' THEN 1 END) as pending_count,
                            COUNT(CASE WHEN Status='Failed' THEN 1 END) as failed_count
                        FROM Payments
                        WHERE ClientID=%s
                    """
                    cursor.execute(query, (client_id,))
                else:
                    query = """
                        SELECT 
                            COUNT(*) as total_payments,
                            SUM(Amount) as total_amount,
                            AVG(Amount) as average_payment,
                            MIN(PaymentDate) as first_payment,
                            MAX(PaymentDate) as last_payment,
                            SUM(CASE WHEN Status='Completed' THEN Amount ELSE 0 END) as completed_amount,
                            SUM(CASE WHEN Status='Pending' THEN Amount ELSE 0 END) as pending_amount,
                            SUM(CASE WHEN Status='Failed' THEN Amount ELSE 0 END) as failed_amount,
                            COUNT(CASE WHEN Status='Completed' THEN 1 END) as completed_count,
                            COUNT(CASE WHEN Status='Pending' THEN 1 END) as pending_count,
                            COUNT(CASE WHEN Status='Failed' THEN 1 END) as failed_count,
                            COUNT(DISTINCT ClientID) as unique_clients
                        FROM Payments
                    """
                    cursor.execute(query)
                
                stats = cursor.fetchone()
                
                # Конвертируем Decimal в float
                if stats:
                    for key in stats:
                        if stats[key] is not None and isinstance(stats[key], (int, float, Decimal)):
                            stats[key] = float(stats[key])
                
                return stats
        except Exception as e:
            print(f"Ошибка получения статистики платежей: {e}")
            return None
    
    def add_payment(self, client_id, amount, payment_method='Банковская карта', description=None, status='Completed'):
        """Добавляет платеж"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем существование клиента
                cursor.execute("SELECT ClientID, Balance FROM Clients WHERE ClientID=%s", (client_id,))
                client = cursor.fetchone()
                
                if not client:
                    return False, "Клиент не найден"
                
                # Создаем запись о платеже
                cursor.execute("""
                    INSERT INTO Payments (ClientID, Amount, PaymentMethod, Status, Description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (client_id, amount, payment_method, status, description or f"Пополнение баланса на {amount} руб."))
                
                payment_id = cursor.lastrowid
                
                # Если платеж успешный, обновляем баланс
                if status == 'Completed':
                    old_balance = float(client['Balance']) if client['Balance'] else 0
                    new_balance = old_balance + amount
                    
                    cursor.execute("UPDATE Clients SET Balance=%s WHERE ClientID=%s", 
                                 (new_balance, client_id))
                    
                    # Записываем в историю баланса
                    cursor.execute("""
                        INSERT INTO BalanceHistory (ClientID, OldBalance, NewBalance, ChangeAmount, ChangeType, Description, RelatedID)
                        VALUES (%s, %s, %s, %s, 'Payment', %s, %s)
                    """, (client_id, old_balance, new_balance, amount,
                         description or f"Платеж #{payment_id}: Пополнение баланса",
                         payment_id))
                    
                    # Создаем уведомление
                    cursor.execute("""
                        INSERT INTO Notifications (ClientID, Title, Message, Type)
                        VALUES (%s, %s, %s, 'Payment')
                    """, (client_id, 
                         f"Баланс пополнен на {amount} руб.",
                         f"Ваш баланс пополнен на {amount} руб. Новый баланс: {new_balance:,.2f} руб."))
                elif status == 'Pending':
                    # Уведомление об ожидании платежа
                    cursor.execute("""
                        INSERT INTO Notifications (ClientID, Title, Message, Type)
                        VALUES (%s, 'Платеж ожидает обработки', %s, 'Payment')
                    """, (client_id, 
                         f"Платеж на сумму {amount} руб. ожидает обработки. Статус будет обновлен после проверки."))
                
                self.connection.commit()
                return True, payment_id
        except Exception as e:
            return False, f"Ошибка обработки платежа: {e}"
    
    def update_payment_status(self, payment_id, status):
        """Обновляет статус платежа"""
        try:
            with self.connection.cursor() as cursor:
                # Получаем информацию о платеже
                cursor.execute("SELECT ClientID, Amount, Status as old_status FROM Payments WHERE PaymentID=%s", (payment_id,))
                payment = cursor.fetchone()
                
                if not payment:
                    return False, "Платеж не найден"
                
                old_status = payment['old_status']
                client_id = payment['ClientID']
                amount = float(payment['Amount'])
                
                # Обновляем статус платежа
                cursor.execute("UPDATE Payments SET Status=%s, UpdatedAt=NOW() WHERE PaymentID=%s", (status, payment_id))
                
                # Если статус изменился на Completed и был не Completed
                if status == 'Completed' and old_status != 'Completed':
                    # Обновляем баланс клиента
                    cursor.execute("SELECT Balance FROM Clients WHERE ClientID=%s", (client_id,))
                    client = cursor.fetchone()
                    
                    if client:
                        old_balance = float(client['Balance']) if client['Balance'] else 0
                        new_balance = old_balance + amount
                        
                        cursor.execute("UPDATE Clients SET Balance=%s WHERE ClientID=%s", 
                                     (new_balance, client_id))
                        
                        # Записываем в историю баланса
                        cursor.execute("""
                            INSERT INTO BalanceHistory (ClientID, OldBalance, NewBalance, ChangeAmount, ChangeType, Description, RelatedID)
                            VALUES (%s, %s, %s, %s, 'Payment', %s, %s)
                        """, (client_id, old_balance, new_balance, amount,
                             f"Платеж #{payment_id} подтвержден",
                             payment_id))
                        
                        # Создаем уведомление
                        cursor.execute("""
                            INSERT INTO Notifications (ClientID, Title, Message, Type)
                            VALUES (%s, 'Платеж подтвержден', %s, 'Payment')
                        """, (client_id, 
                             f"Платеж на сумму {amount} руб. успешно подтвержден. Баланс пополнен."))
                
                self.connection.commit()
                return True, f"Статус платежа обновлен на '{status}'"
        except Exception as e:
            return False, f"Ошибка обновления статуса платежа: {e}"
    
    # ===============================================
    # БАЛАНС И ИСТОРИЯ
    # ===============================================
    
    def get_balance_history(self, client_id, limit=50):
        """Получает историю баланса"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        HistoryID, CreatedAt, OldBalance, NewBalance,
                        ChangeAmount, ChangeType, Description, RelatedID
                    FROM BalanceHistory
                    WHERE ClientID=%s
                    ORDER BY CreatedAt DESC
                    LIMIT %s
                """, (client_id, limit))
                history = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for record in history:
                    if 'OldBalance' in record and record['OldBalance'] is not None:
                        record['OldBalance'] = float(record['OldBalance'])
                    if 'NewBalance' in record and record['NewBalance'] is not None:
                        record['NewBalance'] = float(record['NewBalance'])
                    if 'ChangeAmount' in record and record['ChangeAmount'] is not None:
                        record['ChangeAmount'] = float(record['ChangeAmount'])
                    # Форматируем дату
                    if 'CreatedAt' in record and record['CreatedAt']:
                        # Исправление: проверяем, является ли CreatedAt строкой или datetime
                        if hasattr(record['CreatedAt'], 'strftime'):
                            record['CreatedAt'] = record['CreatedAt'].strftime('%d.%m.%Y %H:%M')
                        else:
                            # Если это строка, пытаемся преобразовать
                            try:
                                dt = datetime.strptime(str(record['CreatedAt']), '%Y-%m-%d %H:%M:%S')
                                record['CreatedAt'] = dt.strftime('%d.%m.%Y %H:%M')
                            except:
                                record['CreatedAt'] = str(record['CreatedAt'])
                
                return history
        except Exception as e:
            print(f"Ошибка получения истории баланса: {e}")
            return []
    
    def adjust_balance(self, client_id, amount, change_type='Correction', description=None):
        """Корректирует баланс клиента"""
        try:
            with self.connection.cursor() as cursor:
                # Получаем текущий баланс
                cursor.execute("SELECT Balance FROM Clients WHERE ClientID=%s", (client_id,))
                client = cursor.fetchone()
                
                if not client:
                    return False, "Клиент не найден"
                
                old_balance = float(client['Balance']) if client['Balance'] else 0
                new_balance = old_balance + amount
                
                # Обновляем баланс
                cursor.execute("UPDATE Clients SET Balance=%s WHERE ClientID=%s", 
                             (new_balance, client_id))
                
                # Записываем в историю баланса
                cursor.execute("""
                    INSERT INTO BalanceHistory (ClientID, OldBalance, NewBalance, ChangeAmount, ChangeType, Description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (client_id, old_balance, new_balance, amount, change_type,
                     description or f"Корректировка баланса на {amount} руб."))
                
                # Создаем уведомление
                cursor.execute("""
                    INSERT INTO Notifications (ClientID, Title, Message, Type)
                    VALUES (%s, %s, %s, 'System')
                """, (client_id, 
                     f"Корректировка баланса",
                     f"Баланс скорректирован на {amount} руб. Новый баланс: {new_balance:,.2f} руб."))
                
                self.connection.commit()
                return True, f"Баланс скорректирован. Новый баланс: {new_balance:,.2f} руб."
        except Exception as e:
            return False, f"Ошибка корректировки баланса: {e}"
    
    # ===============================================
    # УВЕДОМЛЕНИЯ
    # ===============================================
    
    def get_notifications(self, client_id=None, unread_only=False, limit=50):
        """Получает уведомления"""
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM Notifications WHERE 1=1"
                params = []
                
                if client_id:
                    query += " AND ClientID=%s"
                    params.append(client_id)
                
                if unread_only:
                    query += " AND IsRead=FALSE"
                
                query += " ORDER BY CreatedAt DESC"
                
                if limit:
                    query += " LIMIT %s"
                    params.append(limit)
                
                cursor.execute(query, tuple(params))
                notifications = cursor.fetchall()
                
                # Форматируем даты
                for notification in notifications:
                    if 'CreatedAt' in notification and notification['CreatedAt']:
                        # Исправление: безопасное форматирование даты
                        if hasattr(notification['CreatedAt'], 'strftime'):
                            notification['CreatedAt'] = notification['CreatedAt'].strftime('%d.%m.%Y %H:%M')
                        else:
                            try:
                                dt = datetime.strptime(str(notification['CreatedAt']), '%Y-%m-%d %H:%M:%S')
                                notification['CreatedAt'] = dt.strftime('%d.%m.%Y %H:%M')
                            except:
                                notification['CreatedAt'] = str(notification['CreatedAt'])
                    
                    if 'ReadAt' in notification and notification['ReadAt']:
                        if hasattr(notification['ReadAt'], 'strftime'):
                            notification['ReadAt'] = notification['ReadAt'].strftime('%d.%m.%Y %H:%M')
                        else:
                            try:
                                dt = datetime.strptime(str(notification['ReadAt']), '%Y-%m-%d %H:%M:%S')
                                notification['ReadAt'] = dt.strftime('%d.%m.%Y %H:%M')
                            except:
                                notification['ReadAt'] = str(notification['ReadAt'])
                
                return notifications
        except Exception as e:
            print(f"Ошибка получения уведомлений: {e}")
            return []
    
    def get_client_notifications(self, client_id, limit=10):
        """Получает уведомления клиента"""
        return self.get_notifications(client_id=client_id, limit=limit)
    
    def mark_notification_read(self, notification_id):
        """Помечает уведомление как прочитанное"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Notifications 
                    SET IsRead=TRUE, ReadAt=NOW() 
                    WHERE NotificationID=%s
                """, (notification_id,))
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Ошибка обновления уведомления: {e}")
            return False
    
    def mark_all_notifications_read(self, client_id):
        """Помечает все уведомления клиента как прочитанные"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Notifications 
                    SET IsRead=TRUE, ReadAt=NOW() 
                    WHERE ClientID=%s AND IsRead=FALSE
                """, (client_id,))
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Ошибка обновления уведомлений: {e}")
            return False
    
    def create_notification(self, client_id, title, message, notification_type='System', is_important=False):
        """Создает новое уведомление"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Notifications (ClientID, Title, Message, Type, IsImportant)
                    VALUES (%s, %s, %s, %s, %s)
                """, (client_id, title, message, notification_type, is_important))
                
                self.connection.commit()
                return True, "Уведомление создано"
        except Exception as e:
            return False, f"Ошибка создания уведомления: {e}"
    
    # ===============================================
    # УСЛУГИ КЛИЕНТОВ
    # ===============================================
    
    def get_client_services(self, client_id):
        """Получает услуги клиента"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        cs.ClientServiceID, cs.ConnectionID, cs.ServiceID,
                        cs.MonthlyCost, cs.ActivationDate, cs.DeactivationDate,
                        cs.IsActive, cs.CreatedAt, cs.UpdatedAt,
                        s.ServiceName, s.Description as ServiceDescription,
                        t.TariffName
                    FROM ClientServices cs
                    JOIN Services s ON cs.ServiceID = s.ServiceID
                    JOIN Connections c ON cs.ConnectionID = c.ConnectionID
                    JOIN TariffPlans t ON c.TariffID = t.TariffID
                    WHERE c.ClientID=%s
                    ORDER BY cs.ActivationDate DESC
                """, (client_id,))
                
                services = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for service in services:
                    if 'MonthlyCost' in service and service['MonthlyCost'] is not None:
                        service['MonthlyCost'] = float(service['MonthlyCost'])
                
                return services
        except Exception as e:
            print(f"Ошибка получения услуг клиента: {e}")
            return []
    
    def get_available_services(self):
        """Получает все доступные услуги"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ServiceID, ServiceName, MonthlyCost, Description,
                        IsActive, CreatedAt, UpdatedAt
                    FROM Services
                    WHERE IsActive=1
                    ORDER BY ServiceName
                """)
                
                services = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for service in services:
                    if 'MonthlyCost' in service and service['MonthlyCost'] is not None:
                        service['MonthlyCost'] = float(service['MonthlyCost'])
                
                return services
        except Exception as e:
            print(f"Ошибка получения доступных услуг: {e}")
            return []
    
    def add_client_service(self, client_id, service_id, connection_id=None):
        """Добавляет услугу клиенту"""
        try:
            with self.connection.cursor() as cursor:
                # Если connection_id не указан, получаем активное подключение клиента
                if not connection_id:
                    cursor.execute("""
                        SELECT ConnectionID FROM Connections 
                        WHERE ClientID=%s AND Status='Active' 
                        LIMIT 1
                    """, (client_id,))
                    connection = cursor.fetchone()
                    
                    if not connection:
                        return False, "У клиента нет активного подключения"
                    
                    connection_id = connection['ConnectionID']
                
                # Проверяем, подключена ли уже эта услуга
                cursor.execute("""
                    SELECT ClientServiceID FROM ClientServices 
                    WHERE ConnectionID=%s AND ServiceID=%s AND IsActive=1
                """, (connection_id, service_id))
                
                if cursor.fetchone():
                    return False, "Эта услуга уже подключена"
                
                # Получаем стоимость услуги
                cursor.execute("SELECT MonthlyCost, ServiceName FROM Services WHERE ServiceID=%s", (service_id,))
                service_data = cursor.fetchone()
                
                if not service_data:
                    return False, "Услуга не найдена"
                
                service_cost = service_data['MonthlyCost']
                service_name = service_data['ServiceName']
                
                # Подключаем услугу
                cursor.execute("""
                    INSERT INTO ClientServices (ConnectionID, ServiceID, MonthlyCost, ActivationDate, IsActive)
                    VALUES (%s, %s, %s, CURDATE(), 1)
                """, (connection_id, service_id, service_cost))
                
                # Создаем уведомление
                cursor.execute("""
                    INSERT INTO Notifications (ClientID, Title, Message, Type)
                    VALUES (%s, 'Новая услуга подключена', %s, 'Service')
                """, (client_id, 
                     f"Услуга '{service_name}' успешно подключена. Стоимость: {service_cost} руб./мес."))
                
                self.connection.commit()
                return True, "Услуга успешно подключена"
        except Exception as e:
            return False, f"Ошибка подключения услуги: {e}"
    
    def remove_client_service(self, client_service_id):
        """Отключает услугу у клиента"""
        try:
            with self.connection.cursor() as cursor:
                # Получаем информацию об услуге
                cursor.execute("""
                    SELECT cs.ClientServiceID, cs.ConnectionID, cs.ServiceID,
                           s.ServiceName, c.ClientID
                    FROM ClientServices cs
                    JOIN Services s ON cs.ServiceID = s.ServiceID
                    JOIN Connections con ON cs.ConnectionID = con.ConnectionID
                    JOIN Clients c ON con.ClientID = c.ClientID
                    WHERE cs.ClientServiceID=%s
                """, (client_service_id,))
                
                service_info = cursor.fetchone()
                
                if not service_info:
                    return False, "Услуга не найдена"
                
                # Отключаем услугу
                cursor.execute("""
                    UPDATE ClientServices 
                    SET DeactivationDate=CURDATE(), IsActive=0, UpdatedAt=NOW()
                    WHERE ClientServiceID=%s
                """, (client_service_id,))
                
                # Создаем уведомление
                cursor.execute("""
                    INSERT INTO Notifications (ClientID, Title, Message, Type)
                    VALUES (%s, 'Услуга отключена', %s, 'Service')
                """, (service_info['ClientID'], 
                     f"Услуга '{service_info['ServiceName']}' отключена."))
                
                self.connection.commit()
                return True, "Услуга успешно отключена"
        except Exception as e:
            return False, f"Ошибка отключения услуги: {e}"
    
    # ===============================================
    # ТАРИФЫ КЛИЕНТОВ
    # ===============================================
    
    def get_available_tariffs(self):
        """Получает доступные тарифы"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        TariffID, TariffName, DownloadSpeedMbps, UploadSpeedMbps,
                        MonthlyCost, Description, IsActive
                    FROM TariffPlans
                    WHERE IsActive=1
                    ORDER BY MonthlyCost
                """)
                
                tariffs = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for tariff in tariffs:
                    if 'MonthlyCost' in tariff and tariff['MonthlyCost'] is not None:
                        tariff['MonthlyCost'] = float(tariff['MonthlyCost'])
                
                return tariffs
        except Exception as e:
            print(f"Ошибка получения тарифов: {e}")
            return []
    
    def change_client_tariff(self, client_id, tariff_id):
        """Изменяет тариф клиента"""
        try:
            with self.connection.cursor() as cursor:
                # Получаем активное подключение клиента
                cursor.execute("""
                    SELECT ConnectionID, TariffID, MonthlyPayment 
                    FROM Connections 
                    WHERE ClientID=%s AND Status='Active' 
                    LIMIT 1
                """, (client_id,))
                
                connection = cursor.fetchone()
                
                if not connection:
                    return False, "У клиента нет активного подключения"
                
                # Получаем информацию о новом тарифе
                cursor.execute("""
                    SELECT TariffName, MonthlyCost 
                    FROM TariffPlans 
                    WHERE TariffID=%s AND IsActive=1
                """, (tariff_id,))
                
                new_tariff = cursor.fetchone()
                
                if not new_tariff:
                    return False, "Тариф не найден или неактивен"
                
                # Получаем информацию о текущем тарифе
                cursor.execute("""
                    SELECT TariffName, MonthlyCost 
                    FROM TariffPlans 
                    WHERE TariffID=%s
                """, (connection['TariffID'],))
                
                current_tariff = cursor.fetchone()
                
                # Обновляем тариф
                cursor.execute("""
                    UPDATE Connections 
                    SET TariffID=%s, MonthlyPayment=%s, 
                        NextPaymentDate=DATE_ADD(CURDATE(), INTERVAL 1 MONTH),
                        UpdatedAt=NOW()
                    WHERE ConnectionID=%s
                """, (tariff_id, new_tariff['MonthlyCost'], connection['ConnectionID']))
                
                # Создаем уведомление
                current_name = current_tariff['TariffName'] if current_tariff else "предыдущий тариф"
                new_cost = float(new_tariff['MonthlyCost'])
                
                cursor.execute("""
                    INSERT INTO Notifications (ClientID, Title, Message, Type)
                    VALUES (%s, 'Тариф изменен', %s, 'Tariff')
                """, (client_id, 
                     f"Тариф изменен с '{current_name}' на '{new_tariff['TariffName']}'. "
                     f"Новая стоимость: {new_cost} руб./мес."))
                
                self.connection.commit()
                return True, "Тариф успешно изменен"
        except Exception as e:
            return False, f"Ошибка изменения тарифа: {e}"
    
    # ===============================================
    # ПРОФИЛЬ КЛИЕНТА
    # ===============================================
    
    def update_client_profile(self, client_id, phone, email, actual_address):
        """Обновляет профиль клиента"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем уникальность телефона
                cursor.execute("""
                    SELECT ClientID FROM Clients 
                    WHERE PhoneNumber=%s AND ClientID!=%s
                """, (phone, client_id))
                
                if cursor.fetchone():
                    return False, "Этот телефон уже используется другим клиентом"
                
                cursor.execute("""
                    UPDATE Clients SET 
                        PhoneNumber=%s, 
                        Email=%s, 
                        ActualAddress=%s
                    WHERE ClientID=%s
                """, (phone, email or None, actual_address or None, client_id))
                
                self.connection.commit()
                return True, "Профиль обновлен"
        except Exception as e:
            return False, f"Ошибка обновления профиля: {e}"
    
    def change_client_password(self, client_id, current_password, new_password):
        """Изменяет пароль клиента"""
        try:
            with self.connection.cursor() as cursor:
                # Получаем UserID клиента
                cursor.execute("SELECT UserID FROM Clients WHERE ClientID=%s", (client_id,))
                user_result = cursor.fetchone()
                user_id = user_result['UserID'] if user_result else None
                
                if not user_id:
                    return False, "Пользователь не найден"
                
                # Проверяем текущий пароль
                current_hash = hashlib.sha256(current_password.encode()).hexdigest()
                cursor.execute("SELECT password FROM users WHERE id=%s", (user_id,))
                user_data = cursor.fetchone()
                
                if not user_data or current_hash != user_data['password']:
                    return False, "Неверный текущий пароль"
                
                # Обновляем пароль
                new_hash = hashlib.sha256(new_password.encode()).hexdigest()
                cursor.execute("UPDATE users SET password=%s WHERE id=%s", 
                             (new_hash, user_id))
                
                self.connection.commit()
                return True, "Пароль изменен"
        except Exception as e:
            return False, f"Ошибка изменения пароля: {e}"
    
    # ===============================================
    # ОТЧЕТЫ И СТАТИСТИКА
    # ===============================================
    def get_services_report(self):
        """Генерирует отчет по услугам"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        s.ServiceName as Service,
                        s.MonthlyCost as Cost,
                        COUNT(cs.ClientServiceID) as ConnectionCount,
                        COUNT(cs.ClientServiceID) * s.MonthlyCost as TotalRevenue
                    FROM Services s
                    LEFT JOIN ClientServices cs ON s.ServiceID = cs.ServiceID AND cs.IsActive = 1
                    WHERE s.IsActive = 1
                    GROUP BY s.ServiceID, s.ServiceName, s.MonthlyCost
                    ORDER BY ConnectionCount DESC
                """)
                report_data = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for row in report_data:
                    if 'Cost' in row and row['Cost'] is not None:
                        row['Cost'] = float(row['Cost'])
                    if 'TotalRevenue' in row and row['TotalRevenue'] is not None:
                        row['TotalRevenue'] = float(row['TotalRevenue'])
                
                return report_data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации отчета по услугам: {e}")
            return []
    def get_financial_report(self, start_date=None, end_date=None):
        """Генерирует финансовый отчет"""
        try:
            with self.connection.cursor() as cursor:
                query = """
                    SELECT 
                        YEAR(PaymentDate) as Year,
                        MONTH(PaymentDate) as Month,
                        COUNT(*) as PaymentCount,
                        SUM(Amount) as TotalAmount,
                        AVG(Amount) as AveragePayment,
                        PaymentMethod,
                        COUNT(DISTINCT ClientID) as UniqueClients
                    FROM Payments 
                    WHERE Status='Completed'
                """
                params = []
                
                if start_date:
                    query += " AND PaymentDate >= %s"
                    params.append(start_date)
                
                if end_date:
                    query += " AND PaymentDate <= %s"
                    params.append(end_date)
                
                query += """
                    GROUP BY YEAR(PaymentDate), MONTH(PaymentDate), PaymentMethod
                    ORDER BY Year DESC, Month DESC
                """
                
                cursor.execute(query, tuple(params))
                report_data = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for row in report_data:
                    for key in ['TotalAmount', 'AveragePayment']:
                        if row.get(key) is not None:
                            row[key] = float(row[key])
                
                return report_data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка получения финансового отчета: {e}")
            return []
    
    def get_clients_report(self):
        """Генерирует отчет по клиентам"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN IsActive = 1 THEN 'Активные'
                            ELSE 'Неактивные'
                        END as Status,
                        COUNT(*) as ClientCount,
                        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Clients), 2) as Percentage
                    FROM Clients 
                    GROUP BY IsActive
                    ORDER BY Status
                """)
                result = cursor.fetchall()
                
                # Вычисляем общее количество клиентов
                total_clients = 0
                for row in result:
                    total_clients += row['ClientCount']
                
                # Добавляем общее количество в каждую строку (для обратной совместимости)
                for row in result:
                    row['TotalClients'] = total_clients
                
                return result
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка получения отчета по клиентам: {e}")
            return []
    
    def get_clients_report(self):
        """Генерирует отчет по клиентам"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN IsActive = 1 THEN 'Активные'
                            ELSE 'Неактивные'
                        END as Status,
                        COUNT(*) as ClientCount,
                        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Clients), 2) as Percentage
                    FROM Clients 
                    GROUP BY IsActive
                    ORDER BY Status
                """)
                result = cursor.fetchall()
                
                # Вычисляем общее количество клиентов
                total_clients = 0
                for row in result:
                    total_clients += row['ClientCount']
                
                # Добавляем общее количество в каждую строку (для обратной совместимости)
                for row in result:
                    row['TotalClients'] = total_clients
                
                return result
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка получения отчета по клиентам: {e}")
            return []
    
    def get_full_report(self):
        """Генерирует полный отчет"""
        try:
            with self.connection.cursor() as cursor:
                # Общая статистика
                stats = {}
                
                # Количество клиентов
                cursor.execute("""
                    SELECT 
                        COUNT(*) as TotalClients,
                        SUM(CASE WHEN IsActive = 1 THEN 1 ELSE 0 END) as ActiveClients,
                        SUM(CASE WHEN IsActive = 0 THEN 1 ELSE 0 END) as InactiveClients,
                        AVG(Balance) as AverageBalance
                    FROM Clients
                """)
                client_stats = cursor.fetchone()
                stats.update(client_stats)
                
                # Финансовая статистика
                cursor.execute("""
                    SELECT 
                        COUNT(*) as TotalPayments,
                        SUM(Amount) as TotalRevenue,
                        AVG(Amount) as AveragePayment,
                        MIN(PaymentDate) as FirstPayment,
                        MAX(PaymentDate) as LastPayment
                    FROM Payments
                    WHERE Status='Completed'
                """)
                finance_stats = cursor.fetchone()
                stats.update(finance_stats)
                
                # Статистика по подключениям
                cursor.execute("""
                    SELECT 
                        COUNT(*) as TotalConnections,
                        SUM(CASE WHEN Status='Active' THEN 1 ELSE 0 END) as ActiveConnections,
                        SUM(CASE WHEN Status='Suspended' THEN 1 ELSE 0 END) as SuspendedConnections,
                        SUM(CASE WHEN Status='Terminated' THEN 1 ELSE 0 END) as TerminatedConnections
                    FROM Connections
                """)
                connection_stats = cursor.fetchone()
                stats.update(connection_stats)
                
                # Популярные тарифы
                cursor.execute("""
                    SELECT 
                        t.TariffName,
                        COUNT(c.ConnectionID) as ConnectionCount,
                        SUM(c.MonthlyPayment) as MonthlyRevenue
                    FROM TariffPlans t
                    LEFT JOIN Connections c ON t.TariffID = c.TariffID AND c.Status = 'Active'
                    WHERE t.IsActive = 1
                    GROUP BY t.TariffID, t.TariffName
                    ORDER BY ConnectionCount DESC
                    LIMIT 5
                """)
                popular_tariffs = cursor.fetchall()
                
                # Статистика платежей по месяцам
                cursor.execute("""
                    SELECT 
                        DATE_FORMAT(PaymentDate, '%Y-%m') as Period,
                        COUNT(*) as PaymentCount,
                        SUM(Amount) as TotalAmount,
                        AVG(Amount) as AveragePayment
                    FROM Payments 
                    WHERE Status='Completed' AND PaymentDate >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                    GROUP BY DATE_FORMAT(PaymentDate, '%Y-%m')
                    ORDER BY Period DESC
                """)
                payments_stats = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for key in stats:
                    if stats[key] is not None and isinstance(stats[key], (int, float, Decimal)):
                        stats[key] = float(stats[key])
                
                for tariff in popular_tariffs:
                    if 'MonthlyRevenue' in tariff and tariff['MonthlyRevenue'] is not None:
                        tariff['MonthlyRevenue'] = float(tariff['MonthlyRevenue'])
                
                for payment in payments_stats:
                    for key in ['TotalAmount', 'AveragePayment']:
                        if payment.get(key) is not None:
                            payment[key] = float(payment[key])
                
                return {
                    'stats': stats,
                    'popular_tariffs': popular_tariffs,
                    'payments_stats': payments_stats
                }
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка получения полного отчета: {e}")
            return {}
    
    def get_system_statistics(self):
        """Получает системную статистику"""
        try:
            with self.connection.cursor() as cursor:
                stats = {}
                
                # Общее количество записей
                tables = ['users', 'Clients', 'TariffPlans', 'Connections', 'Services', 
                         'ClientServices', 'Payments', 'Notifications']
                
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                        result = cursor.fetchone()
                        stats[f'{table}_count'] = result['count'] if result else 0
                    except:
                        stats[f'{table}_count'] = 0
                
                # Непрочитанные уведомления
                cursor.execute("SELECT COUNT(*) as count FROM Notifications WHERE IsRead=FALSE")
                result = cursor.fetchone()
                stats['unread_notifications'] = result['count'] if result else 0
                
                return stats
        except Exception as e:
            print(f"Ошибка получения системной статистики: {e}")
            return {}
    
    # ===============================================
    # КАПЧА И БЕЗОПАСНОСТЬ
    # ===============================================
    
    def increment_captcha_attempts(self, username):
        """Увеличивает счетчик неудачных попыток капчи для пользователя"""
        try:
            with self.connection.cursor() as cursor:
                # Получаем текущее количество попыток
                cursor.execute("SELECT failed_attempts FROM users WHERE username=%s", (username,))
                result = cursor.fetchone()
                
                if result:
                    current_attempts = result['failed_attempts']
                    new_attempts = current_attempts + 1
                    
                    # Обновляем счетчик попыток
                    cursor.execute("UPDATE users SET failed_attempts=%s WHERE username=%s", 
                                 (new_attempts, username))
                    
                    # Блокируем если достигнут лимит
                    if new_attempts >= 3:
                        cursor.execute("UPDATE users SET is_active=0 WHERE username=%s", (username,))
                    
                    self.connection.commit()
                    return new_attempts
                return 0
        except Exception as e:
            print(f"Ошибка обновления попыток капчи: {e}")
            return 0
    
    def reset_login_attempts(self, username):
        """Сбрасывает счетчик неудачных попыток входа"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("UPDATE users SET failed_attempts=0 WHERE username=%s", (username,))
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Ошибка сброса попыток входа: {e}")
            return False
    
    # ===============================================
    # ЭКСПОРТ ДАННЫХ (ОБНОВЛЕННЫЕ МЕТОДЫ - ТОЛЬКО TXT)
    # ===============================================
    
    def export_payments_txt(self, client_id=None, start_date=None, end_date=None):
        """Экспортирует платежи в TXT формат"""
        payments = self.get_payments(client_id, start_date, end_date)
        
        if not payments:
            return None
        
        # Создаем текстовую строку
        txt_content = "=" * 80 + "\n"
        txt_content += "ОТЧЕТ ПО ПЛАТЕЖАМ\n"
        
        if client_id:
            client = self.get_client_by_id(client_id)
            if client:
                txt_content += f"Клиент: {client['LastName']} {client['FirstName']}\n"
        
        txt_content += f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        txt_content += "=" * 80 + "\n\n"
        
        # Заголовки
        txt_content += f"{'Дата':<20} {'Сумма':<12} {'Способ оплаты':<15} {'Статус':<12} {'Описание':<30}\n"
        txt_content += "-" * 90 + "\n"
        
        # Данные
        total_amount = 0
        for payment in payments:
            # Исправление: безопасное форматирование даты
            payment_date = payment['PaymentDate']
            if hasattr(payment_date, 'strftime'):
                date_str = payment_date.strftime('%d.%m.%Y %H:%M')
            else:
                try:
                    dt = datetime.strptime(str(payment_date), '%Y-%m-%d %H:%M:%S')
                    date_str = dt.strftime('%d.%m.%Y %H:%M')
                except:
                    date_str = str(payment_date)
            
            amount = float(payment['Amount'])
            method = payment['PaymentMethod'][:14]
            status = payment['Status'][:11]
            description = (payment['Description'] or '')[:28]
            
            txt_content += f"{date_str:<20} {amount:<12.2f} {method:<15} {status:<12} {description:<30}\n"
            
            total_amount += amount
        
        # Итоги
        txt_content += "-" * 90 + "\n"
        txt_content += f"ИТОГО: {len(payments)} платежей на сумму {total_amount:,.2f} руб.\n"
        
        return txt_content
    
    def update_client_full(self, client_id, client_data):
        """Полное обновление данных клиента"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем уникальность логина
                cursor.execute("SELECT ClientID FROM Clients WHERE Username=%s AND ClientID!=%s", 
                            (client_data['username'], client_id))
                if cursor.fetchone():
                    return False, "Клиент с указанным логином уже существует"
                
                # Проверяем уникальность телефона
                cursor.execute("SELECT ClientID FROM Clients WHERE PhoneNumber=%s AND ClientID!=%s", 
                            (client_data['phone'], client_id))
                if cursor.fetchone():
                    return False, "Клиент с указанным номером телефона уже существует"
                
                # Получаем UserID клиента
                cursor.execute("SELECT UserID FROM Clients WHERE ClientID=%s", (client_id,))
                user_result = cursor.fetchone()
                user_id = user_result['UserID'] if user_result else None
                
                # Обновляем пользователя
                if user_id:
                    cursor.execute("UPDATE users SET username=%s WHERE id=%s", 
                                (client_data['username'], user_id))
                
                # Обновляем клиента
                query = """
                    UPDATE Clients SET 
                        Username=%s, 
                        FirstName=%s, 
                        LastName=%s, 
                        MiddleName=%s,
                        DateOfBirth=%s, 
                        PhoneNumber=%s, 
                        Email=%s,
                        RegistrationAddress=%s,
                        ActualAddress=%s,
                        PassportSeries=%s,
                        PassportNumber=%s,
                        IssueDate=%s,
                        IssuedBy=%s,
                        IsActive=%s
                    WHERE ClientID=%s
                """
                
                cursor.execute(query, (
                    client_data['username'],
                    client_data['first_name'],
                    client_data['last_name'],
                    client_data.get('middle_name', ''),
                    client_data.get('birth_date'),
                    client_data['phone'],
                    client_data.get('email'),
                    client_data['reg_address'],
                    client_data.get('actual_address', ''),
                    client_data['passport_series'],
                    client_data['passport_number'],
                    client_data.get('issue_date'),
                    client_data.get('issued_by', ''),
                    client_data['is_active'],
                    client_id
                ))
                
                # Создаем уведомление об изменении профиля
                cursor.execute("""
                    INSERT INTO Notifications (ClientID, Title, Message, Type)
                    VALUES (%s, 'Профиль обновлен', 'Ваши личные данные были обновлены.', 'System')
                """, (client_id,))
                
                self.connection.commit()
                return True, "Данные профиля успешно обновлены"
        except Exception as e:
            return False, f"Ошибка обновления профиля: {e}"

    def export_clients_txt(self):
        """Экспортирует клиентов в TXT формат"""
        clients = self.get_clients()
        
        if not clients:
            return None
        
        # Создаем текстовую строку
        txt_content = "=" * 80 + "\n"
        txt_content += "ОТЧЕТ ПО КЛИЕНТАМ\n"
        txt_content += f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        txt_content += "=" * 80 + "\n\n"
        
        # Статистика
        active_clients = sum(1 for c in clients if c['IsActive'])
        inactive_clients = len(clients) - active_clients
        
        txt_content += f"Всего клиентов: {len(clients)}\n"
        txt_content += f"Активных: {active_clients}\n"
        txt_content += f"Неактивных: {inactive_clients}\n\n"
        
        # Заголовки
        txt_content += f"{'ID':<5} {'ФИО':<30} {'Телефон':<15} {'Email':<25} {'Баланс':<12} {'Статус':<10}\n"
        txt_content += "-" * 100 + "\n"
        
        # Данные
        total_balance = 0
        for client in clients:
            full_name = f"{client['LastName']} {client['FirstName']} {client.get('MiddleName', '')}"
            phone = client['PhoneNumber'][:14] if client['PhoneNumber'] else ''
            email = (client['Email'] or '')[:24]
            balance = float(client['Balance'] or 0)
            status = 'Активен' if client['IsActive'] else 'Неактивен'
            
            txt_content += f"{client['ClientID']:<5} {full_name[:29]:<30} {phone:<15} {email:<25} {balance:<12.2f} {status:<10}\n"
            
            total_balance += balance
        
        # Итоги
        txt_content += "-" * 100 + "\n"
        txt_content += f"Суммарный баланс: {total_balance:,.2f} руб.\n"
        txt_content += f"Средний баланс: {total_balance/len(clients):,.2f} руб.\n"
        
        return txt_content
    
    # УДАЛЕНЫ МЕТОДЫ export_payments_csv и export_clients_csv
    
    # ===============================================
    # УТИЛИТЫ
    # ===============================================
    
    def execute_query(self, query, params=None):
        """Выполняет произвольный SQL запрос"""
        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return cursor.rowcount
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None
    
    def get_table_info(self, table_name):
        """Получает информацию о структуре таблицы"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table_name}")
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения информации о таблице: {e}")
            return []
    
    def backup_database(self, backup_path):
        """Создает резервную копию базы данных"""
        try:
            import subprocess
            import datetime
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_path}/backup_{timestamp}.sql"
            
            # Команда для создания дампа базы данных
            cmd = [
                'mysqldump',
                '-u', 'root',
                '-proot',
                'internet__provider',
                '--result-file', backup_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f"Резервная копия создана: {backup_file}"
            else:
                return False, f"Ошибка создания резервной копии: {result.stderr}"
        except Exception as e:
            return False, f"Ошибка создания резервной копии: {e}"
    
    def __del__(self):
        """Деструктор - закрывает соединение при удалении объекта"""
        self.close()

# ===============================================
# Класс для формы регистрации (УПРОЩЕННАЯ ВЕРСИЯ)
# ===============================================

class RegistrationWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = parent.db
        
        self.window = tk.Toplevel(parent.root)
        self.window.title("Регистрация")
        self.window.geometry("450x650")
        self.window.resizable(False, False)
        
        # Основной фрейм с прокруткой
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создаем Canvas и Scrollbar
        canvas = tk.Canvas(main_frame, bg='white')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg='white')
        
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=content_frame, anchor="nw", width=430)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Заголовок
        ttk.Label(content_frame, text="Регистрация", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Создаем поля ввода
        self.create_field(content_frame, "Логин:*", 0)
        self.create_field(content_frame, "Пароль:*", 1, show="*")
        self.create_field(content_frame, "Повторите пароль:*", 2, show="*")
        self.create_field(content_frame, "Имя:*", 3)
        self.create_field(content_frame, "Фамилия:*", 4)
        self.create_field(content_frame, "Телефон:*", 5)
        self.create_field(content_frame, "Email:", 6)
        
        # Адрес регистрации
        ttk.Label(content_frame, text="Адрес регистрации:*").pack(anchor='w', pady=(10, 5))
        self.reg_address = tk.Text(content_frame, height=3, width=40)
        self.reg_address.pack(fill='x', pady=(0, 10))
        
        # Паспортные данные в одной строке
        passport_frame = tk.Frame(content_frame, bg='white')
        passport_frame.pack(fill='x', pady=5)
        
        ttk.Label(passport_frame, text="Паспорт:*").pack(side='left', padx=(0, 10))
        
        ttk.Label(passport_frame, text="Серия:").pack(side='left', padx=(0, 5))
        self.passport_series = ttk.Entry(passport_frame, width=10)
        self.passport_series.pack(side='left', padx=(0, 20))
        
        ttk.Label(passport_frame, text="Номер:").pack(side='left', padx=(0, 5))
        self.passport_number = ttk.Entry(passport_frame, width=15)
        self.passport_number.pack(side='left')
        
        # Информация о полях
        ttk.Label(content_frame, text="* - обязательные поля", 
                 font=("Arial", 9), foreground="gray").pack(anchor='w', pady=10)
        
        # Кнопки
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="Зарегистрировать", 
                  command=self.register, width=20).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=self.window.destroy, width=20).pack(side='left', padx=5)
        
        # Размещаем Canvas и Scrollbar
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Фокус на логин
        self.username.focus()
        
        # Бинд Enter
        self.window.bind('<Return>', lambda event: self.register())
        
        # Центрирование окна
        self.center_window()
    
    def create_field(self, parent, label_text, index, show=None):
        """Создает поле ввода с меткой"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=5)
        
        ttk.Label(frame, text=label_text, width=20).pack(side='left')
        
        if index == 0:  # Логин
            self.username = ttk.Entry(frame, width=25, show=show)
            self.username.pack(side='left')
        elif index == 1:  # Пароль
            self.password = ttk.Entry(frame, width=25, show=show)
            self.password.pack(side='left')
        elif index == 2:  # Подтверждение пароля
            self.confirm_password = ttk.Entry(frame, width=25, show=show)
            self.confirm_password.pack(side='left')
        elif index == 3:  # Имя
            self.first_name = ttk.Entry(frame, width=25, show=show)
            self.first_name.pack(side='left')
        elif index == 4:  # Фамилия
            self.last_name = ttk.Entry(frame, width=25, show=show)
            self.last_name.pack(side='left')
        elif index == 5:  # Телефон
            self.phone = ttk.Entry(frame, width=25, show=show)
            self.phone.pack(side='left')
        elif index == 6:  # Email
            self.email = ttk.Entry(frame, width=25, show=show)
            self.email.pack(side='left')
    
    def center_window(self):
        """Центрирует окно на экране"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def register(self):
        """Обработка регистрации"""
        # Собираем данные
        client_data = {
            'username': self.username.get().strip(),
            'password': self.password.get(),
            'first_name': self.first_name.get().strip(),
            'last_name': self.last_name.get().strip(),
            'middle_name': '',
            'birth_date': None,
            'passport_series': self.passport_series.get().strip(),
            'passport_number': self.passport_number.get().strip(),
            'issue_date': None,
            'issued_by': '',
            'reg_address': self.reg_address.get("1.0", tk.END).strip(),
            'actual_address': '',
            'phone': self.phone.get().strip(),
            'email': self.email.get().strip() or None
        }
        
        # Простая проверка
        errors = []
        
        if not client_data['username']:
            errors.append("Введите логин")
        elif len(client_data['username']) < 3:
            errors.append("Логин должен содержать минимум 3 символа")
        
        if not client_data['password']:
            errors.append("Введите пароль")
        elif len(client_data['password']) < 6:
            errors.append("Пароль должен содержать минимум 6 символов")
        elif client_data['password'] != self.confirm_password.get():
            errors.append("Пароли не совпадают")
        
        if not client_data['first_name']:
            errors.append("Введите имя")
        if not client_data['last_name']:
            errors.append("Введите фамилию")
        if not client_data['phone']:
            errors.append("Введите телефон")
        if not client_data['reg_address']:
            errors.append("Введите адрес регистрации")
        if not client_data['passport_series']:
            errors.append("Введите серию паспорта")
        if not client_data['passport_number']:
            errors.append("Введите номер паспорта")
        
        if errors:
            messagebox.showwarning("Ошибка", "\n".join(errors))
            return
        
        # Регистрация
        success, msg = self.db.add_client(client_data)
        
        if success:
            messagebox.showinfo("Успех", "Регистрация завершена успешно!")
            self.window.destroy()
        else:
            messagebox.showerror("Ошибка", msg)

# ===============================================
# Класс для окна авторизации
# ===============================================

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Авторизация - Интернет-провайдер")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        # Центрирование окна
        self.root.eval('tk::PlaceWindow . center')
        
        try:
            self.db = Database()
        except:
            self.root.destroy()
            return
            
        # Создание основного фрейма
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        ttk.Label(main_frame, text="Авторизация", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )
        
        # Поле логина
        ttk.Label(main_frame, text="Логин:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username = ttk.Entry(main_frame, width=25)
        self.username.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=(tk.W, tk.E))
        
        # Поле пароля
        ttk.Label(main_frame, text="Пароль:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password = ttk.Entry(main_frame, show="*", width=25)
        self.password.grid(row=2, column=1, padx=(10, 0), pady=5, sticky=(tk.W, tk.E))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Войти", command=self.login, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Регистрация", command=self.open_registration, width=15).pack(side=tk.LEFT, padx=5)
        
        # Обязательные поля
        ttk.Label(main_frame, text="* - обязательные поля", foreground="gray", font=("Arial", 8)).grid(
            row=4, column=0, columnspan=2
        )
        
        # Бинд Enter для удобства
        self.root.bind('<Return>', lambda event: self.login())
        
        # Фокус на поле логина
        self.username.focus()
    
    def open_registration(self):
        RegistrationWindow(self)
    
    def login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        
        # Проверка обязательных полей
        if not username or not password:
            messagebox.showwarning("Ошибка", "Поля 'Логин' и 'Пароль' обязательны для заполнения")
            return
            
        auth_result = self.db.auth(username, password)
        
        if auth_result == "blocked":
            messagebox.showerror("Ошибка", "Вы заблокированы. Обратитесь к администратору")
            return
        
        if auth_result:
            # Показываем капчу после успешной аутентификации
            captcha = PuzzleCaptcha()
            captcha_success = captcha.run()
            
            if captcha_success:
                messagebox.showinfo("Успех", "Вы успешно авторизовались")
                self.root.withdraw()
                if auth_result['role'] == 'admin':
                    AdminPanelWindow(self, auth_result)
                else:
                    # Получаем ID клиента
                    client_info = self.db.get_client_by_username(username)
                    if client_info:
                        auth_result['client_id'] = client_info['ClientID']
                    ClientMenuWindow(self, auth_result)
            else:
                # Увеличиваем счетчик неудачных попыток капчи для этого пользователя
                new_attempts = self.db.increment_captcha_attempts(username)
                messagebox.showerror("Ошибка", f"Капча не пройдена. Неудачных попыток: {new_attempts}/3")
                
                if new_attempts >= 3:
                    messagebox.showerror("Ошибка", "Вы заблокированы. Обратитесь к администратору")
        else:
            messagebox.showerror("Ошибка", "Вы ввели неверный логин или пароль")

# ===============================================
# Класс для панели администратора
# ===============================================

class AdminPanelWindow:
    def __init__(self, login_window, user):
        self.login_window = login_window
        self.db = login_window.db
        self.user = user
        
        self.root = tk.Toplevel()
        self.root.title(f"Панель администратора - {user['username']}")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)
        
        # Создаем Notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создаем вкладки
        self.create_users_tab()
        self.create_clients_tab()
        self.create_tariffs_tab()
        self.create_services_tab()
        self.create_reports_tab()
        
        # Кнопка выхода
        ttk.Button(self.root, text="Выйти", command=self.logout, width=15).pack(pady=10)
        
        # Обработчик смены вкладок
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Переменная для хранения текущего отчета
        self.current_report_text = ""
        self.current_report_title = ""
    
    def create_users_tab(self):
        # Вкладка управления пользователями
        users_frame = ttk.Frame(self.notebook)
        self.notebook.add(users_frame, text="Пользователи")
        
        # Заголовок
        ttk.Label(users_frame, text="Управление пользователями", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Фрейм для добавления пользователя
        add_frame = ttk.LabelFrame(users_frame, text="Добавить нового пользователя", padding="10")
        add_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(add_frame, text="Логин:").grid(row=0, column=0, padx=5, pady=5)
        self.new_user = ttk.Entry(add_frame, width=15)
        self.new_user.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Пароль:").grid(row=0, column=2, padx=5, pady=5)
        self.new_pass = ttk.Entry(add_frame, width=15)
        self.new_pass.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Роль:").grid(row=0, column=4, padx=5, pady=5)
        self.new_role = ttk.Combobox(add_frame, values=["user", "admin"], state="readonly", width=10)
        self.new_role.set("user")
        self.new_role.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Button(add_frame, text="Добавить", command=self.add_user).grid(row=0, column=6, padx=5, pady=5)
        
        # Список пользователей
        columns = ("id", "user", "role", "active", "attempts", "last_login", "has_client", "client_id")
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show="headings", height=15)
        
        self.users_tree.heading("id", text="ID")
        self.users_tree.heading("user", text="Логин")
        self.users_tree.heading("role", text="Роль")
        self.users_tree.heading("active", text="Активен")
        self.users_tree.heading("attempts", text="Неудачные попытки")
        self.users_tree.heading("last_login", text="Последний вход")
        self.users_tree.heading("has_client", text="Есть клиент")
        self.users_tree.heading("client_id", text="ID клиента")
        
        self.users_tree.column("id", width=50)
        self.users_tree.column("user", width=150)
        self.users_tree.column("role", width=100)
        self.users_tree.column("active", width=80)
        self.users_tree.column("attempts", width=120)
        self.users_tree.column("last_login", width=120)
        self.users_tree.column("has_client", width=100)
        self.users_tree.column("client_id", width=100)
        
        # Скрываем колонку client_id, она нужна только для внутреннего использования
        self.users_tree.column("client_id", width=0, stretch=False, minwidth=0)
        
        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(users_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill='y', padx=(0, 10), pady=10)
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(users_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Обновить", command=self.load_users).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Разблокировать", command=self.unblock_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_user, width=15).pack(side=tk.LEFT, padx=5)
    
    def create_clients_tab(self):
        # Вкладка управления клиентами
        clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(clients_frame, text="Клиенты")
        
        # Заголовок
        ttk.Label(clients_frame, text="Управление клиентами", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(clients_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Добавить клиента", command=self.add_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.load_clients).pack(side=tk.LEFT, padx=5)
        
        # Список клиентов
        columns = ("id", "username", "name", "phone", "email", "balance", "active")
        self.clients_tree = ttk.Treeview(clients_frame, columns=columns, show="headings", height=20)
        
        self.clients_tree.heading("id", text="ID")
        self.clients_tree.heading("username", text="Логин")
        self.clients_tree.heading("name", text="ФИО")
        self.clients_tree.heading("phone", text="Телефон")
        self.clients_tree.heading("email", text="Email")
        self.clients_tree.heading("balance", text="Баланс")
        self.clients_tree.heading("active", text="Активен")
        
        self.clients_tree.column("id", width=50)
        self.clients_tree.column("username", width=100)
        self.clients_tree.column("name", width=150)
        self.clients_tree.column("phone", width=100)
        self.clients_tree.column("email", width=150)
        self.clients_tree.column("balance", width=80)
        self.clients_tree.column("active", width=80)
        
        # Scrollbar для таблица
        scrollbar = ttk.Scrollbar(clients_frame, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)
        
        self.clients_tree.pack(side=tk.LEFT, fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill='y', padx=(0, 10), pady=10)
        
        # Дополнительные функции
        extra_frame = ttk.Frame(clients_frame)
        extra_frame.pack(pady=10)
        
        ttk.Button(extra_frame, text="Пополнить баланс", command=self.add_client_balance).pack(side=tk.LEFT, padx=5)
        ttk.Button(extra_frame, text="Изменить тариф", command=self.change_client_tariff_admin).pack(side=tk.LEFT, padx=5)
    
    def create_tariffs_tab(self):
        # Вкладка управления тарифами
        tariffs_frame = ttk.Frame(self.notebook)
        self.notebook.add(tariffs_frame, text="Тарифы")
        
        # Заголовок
        ttk.Label(tariffs_frame, text="Управление тарифными планами", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(tariffs_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Добавить тариф", command=self.add_tariff).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_tariff).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_tariff).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.load_tariffs).pack(side=tk.LEFT, padx=5)
        
        # Список тарифов
        columns = ("id", "name", "download", "upload", "cost", "active")
        self.tariffs_tree = ttk.Treeview(tariffs_frame, columns=columns, show="headings", height=20)
        
        self.tariffs_tree.heading("id", text="ID")
        self.tariffs_tree.heading("name", text="Название")
        self.tariffs_tree.heading("download", text="Скорость ↓")
        self.tariffs_tree.heading("upload", text="Скорость ↑")
        self.tariffs_tree.heading("cost", text="Стоимость")
        self.tariffs_tree.heading("active", text="Активен")
        
        self.tariffs_tree.column("id", width=50)
        self.tariffs_tree.column("name", width=150)
        self.tariffs_tree.column("download", width=80)
        self.tariffs_tree.column("upload", width=80)
        self.tariffs_tree.column("cost", width=100)
        self.tariffs_tree.column("active", width=80)
        
        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(tariffs_frame, orient=tk.VERTICAL, command=self.tariffs_tree.yview)
        self.tariffs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.tariffs_tree.pack(side=tk.LEFT, fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill='y', padx=(0, 10), pady=10)
    
    def create_services_tab(self):
        # Вкладка управления услугами
        services_frame = ttk.Frame(self.notebook)
        self.notebook.add(services_frame, text="Услуги")
        
        # Заголовок
        ttk.Label(services_frame, text="Управление услугами", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(services_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Добавить услугу", command=self.add_service).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_service).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_service).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.load_services).pack(side=tk.LEFT, padx=5)
        
        # Список услуг
        columns = ("id", "name", "cost", "active")
        self.services_tree = ttk.Treeview(services_frame, columns=columns, show="headings", height=20)
        
        self.services_tree.heading("id", text="ID")
        self.services_tree.heading("name", text="Название")
        self.services_tree.heading("cost", text="Стоимость")
        self.services_tree.heading("active", text="Активна")
        
        self.services_tree.column("id", width=50)
        self.services_tree.column("name", width=200)
        self.services_tree.column("cost", width=100)
        self.services_tree.column("active", width=80)
        
        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(services_frame, orient=tk.VERTICAL, command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=scrollbar.set)
        
        self.services_tree.pack(side=tk.LEFT, fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill='y', padx=(0, 10), pady=10)
    
    def create_reports_tab(self):
        """Создает вкладку отчетов с улучшенным интерфейсом"""
        reports_frame = tk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Отчеты")
        
        # Верхняя панель с кнопками
        top_frame = tk.Frame(reports_frame, bg='white')
        top_frame.pack(fill='x', pady=10, padx=10)
        
        # Панель выбора типа отчета
        left_panel = tk.Frame(top_frame, bg='white')
        left_panel.pack(side='left')
        
        ttk.Label(left_panel, text="Тип отчета:", background='white').pack(side='left', padx=5)
        
        self.report_type_var = tk.StringVar(value="financial")
        report_types = ttk.Combobox(left_panel, 
                                   textvariable=self.report_type_var,
                                   values=["Финансовый", "Клиенты", "Услуги", "Полный", "Тарифы", "Платежи"],
                                   state="readonly",
                                   width=15)
        report_types.pack(side='left', padx=5)
        
        ttk.Button(left_panel, text="Сгенерировать", 
                  command=self.generate_selected_report,
                  width=15).pack(side='left', padx=5)
        
        # Кнопки управления справа
        right_panel = tk.Frame(top_frame, bg='white')
        right_panel.pack(side='right')
        
        ttk.Button(right_panel, text="Сохранить как TXT", 
                  command=self.save_report_as_text,
                  width=18).pack(side='left', padx=2)
        
        ttk.Button(right_panel, text="Очистить", 
                  command=self.clear_report,
                  width=10).pack(side='left', padx=2)
        
        # Область просмотра отчета
        view_frame = tk.Frame(reports_frame, bg='white')
        view_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Текстовая область с прокруткой
        text_frame = tk.Frame(view_frame, bg='white')
        text_frame.pack(fill='both', expand=True)
        
        # Заголовок отчета
        self.report_title_label = tk.Label(text_frame, 
                                          text="Выберите тип отчета и нажмите 'Сгенерировать'",
                                          font=("Arial", 12, "bold"),
                                          bg='white',
                                          fg='#2c3e50')
        self.report_title_label.pack(anchor='w', pady=(0, 10), padx=5)
        
        # Текст отчета с моноширинным шрифтом
        text_container = tk.Frame(text_frame, bg='white', relief='sunken', borderwidth=1)
        text_container.pack(fill='both', expand=True)
        
        # Создаем Text виджет с прокруткой
        self.report_text = tk.Text(text_container,
                                  wrap='word',
                                  font=('Courier New', 10),
                                  bg='white',
                                  fg='black',
                                  height=20,
                                  relief='flat')
        
        scrollbar_y = ttk.Scrollbar(text_container,
                                   orient='vertical',
                                   command=self.report_text.yview)
        
        scrollbar_x = ttk.Scrollbar(text_container,
                                   orient='horizontal',
                                   command=self.report_text.xview)
        
        self.report_text.configure(yscrollcommand=scrollbar_y.set,
                                  xscrollcommand=scrollbar_x.set,
                                  wrap='none')  # Отключаем перенос для таблиц
        
        # Размещаем элементы
        self.report_text.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)
        
        # Делаем текст только для чтения
        self.report_text.config(state='disabled')
    
    def on_tab_changed(self, event):
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == "Пользователи":
            self.load_users()
        elif current_tab == "Клиенты":
            self.load_clients()
        elif current_tab == "Тарифы":
            self.load_tariffs()
        elif current_tab == "Услуги":
            self.load_services()
        elif current_tab == "Отчеты":
            self.clear_report()
    
    # Методы для работы с пользователями
    def load_users(self):
        """Загружает список пользователей с информацией о связанных клиентах"""
        for i in self.users_tree.get_children():
            self.users_tree.delete(i)
        
        try:
            users = self.db.get_users()
            for user in users:
                # Форматируем дату последнего входа
                if user['last_login'] and hasattr(user['last_login'], 'strftime'):
                    last_login = user['last_login'].strftime('%d.%m.%Y %H:%M')
                else:
                    last_login = 'Никогда'
                
                # Определяем, есть ли связанный клиент
                has_client = 'Да' if user['client_id'] else 'Нет'
                client_id = user['client_id'] if user['client_id'] else ''
                
                # Вставляем данные в таблицу
                self.users_tree.insert("", "end", values=(
                    user['id'], 
                    user['username'], 
                    user['role'], 
                    "Да" if user['is_active'] else "Нет",
                    user['failed_attempts'],
                    last_login,
                    has_client,
                    client_id
                ))
        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")
    
    def add_user(self):
        username = self.new_user.get().strip()
        password = self.new_pass.get().strip()
        role = self.new_role.get()
        
        if not username or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль")
            return
            
        success, msg = self.db.add_user(username, password, role)
        messagebox.showinfo("Успех" if success else "Ошибка", msg)
        if success:
            self.new_user.delete(0, "end")
            self.new_pass.delete(0, "end")
            self.load_users()
    
    def edit_user(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пользователя")
            return
        
        user_data = self.users_tree.item(selected[0])['values']
        self.open_edit_user_window(user_data)
    
    def delete_user(self):
        """Удаление пользователя с подтверждением"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пользователя для удаления")
            return
        
        user_data = self.users_tree.item(selected[0])['values']
        user_id = user_data[0]
        username = user_data[1]
        has_client = user_data[6]  # 'Да' или 'Нет'
        client_id = user_data[7]  # ID клиента или пустая строка
        
        # Формируем сообщение подтверждения
        message_text = f"Вы уверены, что хотите удалить пользователя '{username}' (ID: {user_id})?\n\n"
        
        if has_client == 'Да' and client_id:
            message_text += f"⚠️ У пользователя есть связанный клиент (ID: {client_id}), который также будет удален!\n"
            message_text += "Это удалит все данные клиента (платежи, подключения, уведомления и т.д.)\n\n"
        
        message_text += "Это действие нельзя отменить!"
        
        # Диалог подтверждения
        confirm = messagebox.askyesno(
            "Подтверждение удаления", 
            message_text,
            icon='warning'
        )
        
        if not confirm:
            return
        
        # Удаление пользователя
        success, msg = self.db.delete_user(user_id)
        
        if success:
            messagebox.showinfo("Успех", msg)
            # Обновляем обе таблицы
            self.load_users()
            self.load_clients()
        else:
            messagebox.showerror("Ошибка", msg)
    
    def unblock_user(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пользователя")
            return
        
        user_data = self.users_tree.item(selected[0])['values']
        success, msg = self.db.unblock_user(user_data[0])
        messagebox.showinfo("Успех" if success else "Ошибка", msg)
        if success:
            self.load_users()
    
    def open_edit_user_window(self, user_data):
        window = tk.Toplevel(self.root)
        window.title("Редактирование пользователя")
        window.geometry("300x200")
        window.resizable(False, False)
        
        main_frame = ttk.Frame(window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="Логин:*").grid(row=0, column=0, sticky=tk.W, pady=10)
        username_entry = ttk.Entry(main_frame, width=20)
        username_entry.insert(0, user_data[1])
        username_entry.grid(row=0, column=1, padx=(10, 0), pady=10)
        
        ttk.Label(main_frame, text="Роль:*").grid(row=1, column=0, sticky=tk.W, pady=10)
        role_combo = ttk.Combobox(main_frame, values=["admin", "user"], state="readonly", width=17)
        role_combo.set(user_data[2])
        role_combo.grid(row=1, column=1, padx=(10, 0), pady=10)
        
        active_var = tk.BooleanVar(value=user_data[3]=="Да")
        ttk.Checkbutton(main_frame, text="Активен", variable=active_var).grid(row=2, column=0, columnspan=2, pady=10)
        
        def save():
            if not username_entry.get().strip():
                messagebox.showwarning("Ошибка", "Введите логин")
                return
                
            success, msg = self.db.update_user(
                user_data[0], username_entry.get().strip(), role_combo.get(), active_var.get()
            )
            messagebox.showinfo("Успех" if success else "Ошибка", msg)
            if success:
                self.load_users()
                window.destroy()
        
        ttk.Button(main_frame, text="Сохранить", command=save, width=15).grid(row=3, column=0, columnspan=2, pady=10)
    
    # Методы для работы с клиентами
    def load_clients(self):
        for i in self.clients_tree.get_children():
            self.clients_tree.delete(i)
        for client in self.db.get_clients():
            self.clients_tree.insert("", "end", values=(
                client['ClientID'],
                client['Username'],
                f"{client['LastName']} {client['FirstName']}",
                client['PhoneNumber'],
                client['Email'] or '',
                f"{client['Balance']:,.2f}" if client['Balance'] else "0.00",
                "Да" if client['IsActive'] else "Нет"
            ))
    
    def add_client(self):
        RegistrationWindow(self)
        # После закрытия окна регистрации обновляем список
        self.load_clients()
    
    def edit_client(self):
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента")
            return
        
        client_data = self.clients_tree.item(selected[0])['values']
        self.open_edit_client_window(client_data)
    
    def delete_client(self):
        """Удаление клиента с подтверждением"""
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента для удаления")
            return
        
        client_data = self.clients_tree.item(selected[0])['values']
        client_id = client_data[0]
        client_name = client_data[2]
        username = client_data[1]
        
        # Диалог подтверждения
        confirm = messagebox.askyesno(
            "Подтверждение удаления", 
            f"Вы уверены, что хотите удалить клиента '{client_name}' (ID: {client_id})?\n\n"
            f"Логин: {username}\n\n"
            "Это действие удалит:\n"
            "  • Данные клиента\n"
            "  • Связанного пользователя\n"
            "  • Все платежи клиента\n"
            "  • Все подключения клиента\n"
            "  • Все уведомления клиента\n\n"
            "Это действие нельзя отменить!",
            icon='warning'
        )
        
        if not confirm:
            return
        
        # Удаление клиента
        success, msg = self.db.delete_client(client_id)
        
        if success:
            messagebox.showinfo("Успех", msg)
            # Обновляем обе таблицы
            self.load_clients()
            self.load_users()
        else:
            messagebox.showerror("Ошибка", msg)
    
    def add_client_balance(self):
        """Пополнение баланса клиента администратором"""
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента")
            return
        
        client_data = self.clients_tree.item(selected[0])['values']
        client_id = client_data[0]
        client_name = client_data[2]
        
        # Диалог для ввода суммы
        amount_str = simpledialog.askstring("Пополнение баланса", 
                                          f"Пополнение баланса клиента: {client_name}\nВведите сумму:")
        
        if not amount_str:
            return
            
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Ошибка", "Сумма должна быть положительной")
                return
            
            success, payment_id = self.db.add_payment(
                client_id, amount, "Администратор", f"Пополнение баланса администратором на {amount} руб."
            )
            
            if success:
                messagebox.showinfo("Успех", f"Баланс клиента пополнен на {amount} руб.")
                self.load_clients()
            else:
                messagebox.showerror("Ошибка", payment_id)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")
    
    def change_client_tariff_admin(self):
        """Изменение тарифа клиента администратором"""
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента")
            return
        
        client_data = self.clients_tree.item(selected[0])['values']
        client_id = client_data[0]
        client_name = client_data[2]
        
        # Получаем доступные тарифы
        tariffs = self.db.get_available_tariffs()
        if not tariffs:
            messagebox.showwarning("Ошибка", "Нет доступных тарифов")
            return
        
        # Создаем окно выбора тарифа
        tariff_window = tk.Toplevel(self.root)
        tariff_window.title(f"Смена тарифа для {client_name}")
        tariff_window.geometry("400x300")
        
        main_frame = ttk.Frame(tariff_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Выберите новый тариф:", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Список тарифов
        tariff_var = tk.StringVar()
        tariff_listbox = tk.Listbox(main_frame, height=10)
        tariff_listbox.pack(fill='both', expand=True, pady=10)
        
        for tariff in tariffs:
            tariff_listbox.insert(tk.END, 
                f"{tariff['TariffName']} - {tariff['DownloadSpeedMbps']}/{tariff['UploadSpeedMbps']} Мбит/с - {tariff['MonthlyCost']} руб.")
        
        def apply_tariff():
            selected_index = tariff_listbox.curselection()
            if not selected_index:
                messagebox.showwarning("Ошибка", "Выберите тариф")
                return
            
            selected_tariff = tariffs[selected_index[0]]
            
            success, msg = self.db.change_client_tariff(client_id, selected_tariff['TariffID'])
            
            if success:
                messagebox.showinfo("Успех", f"Тариф клиента изменен на '{selected_tariff['TariffName']}'")
                tariff_window.destroy()
            else:
                messagebox.showerror("Ошибка", msg)
        
        ttk.Button(main_frame, text="Применить", command=apply_tariff).pack()
    
    def open_edit_client_window(self, client_data):
        window = tk.Toplevel(self.root)
        window.title("Редактирование клиента")
        window.geometry("400x350")
        window.resizable(False, False)
        
        main_frame = ttk.Frame(window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        row = 0
        
        ttk.Label(main_frame, text="Логин:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        username_entry = ttk.Entry(main_frame, width=25)
        username_entry.insert(0, client_data[1])
        username_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        # Разделяем ФИО
        name_parts = client_data[2].split()
        last_name = name_parts[0] if len(name_parts) > 0 else ""
        first_name = name_parts[1] if len(name_parts) > 1 else ""
        
        ttk.Label(main_frame, text="Имя:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        first_name_entry = ttk.Entry(main_frame, width=25)
        first_name_entry.insert(0, first_name)
        first_name_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Фамилия:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        last_name_entry = ttk.Entry(main_frame, width=25)
        last_name_entry.insert(0, last_name)
        last_name_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Телефон:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(main_frame, width=25)
        phone_entry.insert(0, client_data[3])
        phone_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(main_frame, width=25)
        email_entry.insert(0, client_data[4])
        email_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Фактический адрес:").grid(row=row, column=0, sticky=tk.W, pady=5)
        address_entry = tk.Text(main_frame, width=25, height=3)
        address_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        active_var = tk.BooleanVar(value=client_data[6]=="Да")
        ttk.Checkbutton(main_frame, text="Активен", variable=active_var).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        def save():
            client_info = {
                'username': username_entry.get().strip(),
                'first_name': first_name_entry.get().strip(),
                'last_name': last_name_entry.get().strip(),
                'phone': phone_entry.get().strip(),
                'email': email_entry.get().strip(),
                'actual_address': address_entry.get("1.0", tk.END).strip(),
                'is_active': active_var.get()
            }
            
            success, msg = self.db.update_client(client_data[0], client_info)
            messagebox.showinfo("Успех" if success else "Ошибка", msg)
            if success:
                self.load_clients()
                window.destroy()
        
        ttk.Button(main_frame, text="Сохранить", command=save, width=15).grid(row=row, column=0, columnspan=2, pady=10)
    
    # Методы для работы с тарифами
    def load_tariffs(self):
        for i in self.tariffs_tree.get_children():
            self.tariffs_tree.delete(i)
        for tariff in self.db.get_tariffs():
            self.tariffs_tree.insert("", "end", values=(
                tariff['TariffID'],
                tariff['TariffName'],
                f"{tariff['DownloadSpeedMbps']} Мбит/с",
                f"{tariff['UploadSpeedMbps']} Мбит/с",
                f"{tariff['MonthlyCost']} руб.",
                "Да" if tariff['IsActive'] else "Нет"
            ))
    
    def add_tariff(self):
        window = tk.Toplevel(self.root)
        window.title("Добавление тарифа")
        window.geometry("400x300")
        window.resizable(False, False)
        
        main_frame = ttk.Frame(window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        row = 0
        
        ttk.Label(main_frame, text="Название:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(main_frame, width=25)
        name_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Скорость загрузки:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        download_entry = ttk.Entry(main_frame, width=25)
        download_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Скорость отдачи:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        upload_entry = ttk.Entry(main_frame, width=25)
        upload_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Стоимость:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        cost_entry = ttk.Entry(main_frame, width=25)
        cost_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Описание:").grid(row=row, column=0, sticky=tk.W, pady=5)
        desc_entry = tk.Text(main_frame, width=25, height=3)
        desc_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        def save():
            try:
                tariff_info = {
                    'name': name_entry.get().strip(),
                    'download_speed': int(download_entry.get().strip()),
                    'upload_speed': int(upload_entry.get().strip()),
                    'monthly_cost': float(cost_entry.get().strip()),
                    'description': desc_entry.get("1.0", tk.END).strip()
                }
                
                success, msg = self.db.add_tariff(tariff_info)
                messagebox.showinfo("Успех" if success else "Ошибка", msg)
                if success:
                    self.load_tariffs()
                    window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте правильность ввода числовых значений")
        
        ttk.Button(main_frame, text="Сохранить", command=save, width=15).grid(row=row, column=0, columnspan=2, pady=10)
    
    def edit_tariff(self):
        selected = self.tariffs_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите тариф")
            return
        
        tariff_data = self.tariffs_tree.item(selected[0])['values']
        self.open_edit_tariff_window(tariff_data)
    
    def delete_tariff(self):
        selected = self.tariffs_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите тариф")
            return
        
        tariff_data = self.tariffs_tree.item(selected[0])['values']
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранный тариф?"):
            success, msg = self.db.delete_tariff(tariff_data[0])
            messagebox.showinfo("Успех" if success else "Ошибка", msg)
            if success:
                self.load_tariffs()
    
    def open_edit_tariff_window(self, tariff_data):
        window = tk.Toplevel(self.root)
        window.title("Редактирование тарифа")
        window.geometry("400x350")
        window.resizable(False, False)
        
        main_frame = ttk.Frame(window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        row = 0
        
        ttk.Label(main_frame, text="Название:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(main_frame, width=25)
        name_entry.insert(0, tariff_data[1])
        name_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        # Извлекаем числовые значения из строк
        download_speed = int(tariff_data[2].split()[0])
        upload_speed = int(tariff_data[3].split()[0])
        monthly_cost = float(tariff_data[4].split()[0])
        
        ttk.Label(main_frame, text="Скорость загрузки:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        download_entry = ttk.Entry(main_frame, width=25)
        download_entry.insert(0, str(download_speed))
        download_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Скорость отдачи:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        upload_entry = ttk.Entry(main_frame, width=25)
        upload_entry.insert(0, str(upload_speed))
        upload_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Стоимость:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        cost_entry = ttk.Entry(main_frame, width=25)
        cost_entry.insert(0, str(monthly_cost))
        cost_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Описание:").grid(row=row, column=0, sticky=tk.W, pady=5)
        desc_entry = tk.Text(main_frame, width=25, height=4)
        desc_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        active_var = tk.BooleanVar(value=tariff_data[5]=="Да")
        ttk.Checkbutton(main_frame, text="Активен", variable=active_var).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        def save():
            try:
                tariff_info = {
                    'name': name_entry.get().strip(),
                    'download_speed': int(download_entry.get().strip()),
                    'upload_speed': int(upload_entry.get().strip()),
                    'monthly_cost': float(cost_entry.get().strip()),
                    'description': desc_entry.get("1.0", tk.END).strip(),
                    'is_active': active_var.get()
                }
                
                success, msg = self.db.update_tariff(tariff_data[0], tariff_info)
                messagebox.showinfo("Успех" if success else "Ошибка", msg)
                if success:
                    self.load_tariffs()
                    window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте правильность ввода числовых значений")
        
        ttk.Button(main_frame, text="Сохранить", command=save, width=15).grid(row=row, column=0, columnspan=2, pady=10)
    
    # Методы для работы с услугами
    def load_services(self):
        for i in self.services_tree.get_children():
            self.services_tree.delete(i)
        for service in self.db.get_services():
            self.services_tree.insert("", "end", values=(
                service['ServiceID'],
                service['ServiceName'],
                f"{service['MonthlyCost']} руб.",
                "Да" if service['IsActive'] else "Нет"
            ))
    
    def add_service(self):
        window = tk.Toplevel(self.root)
        window.title("Добавление услуги")
        window.geometry("400x250")
        window.resizable(False, False)
        
        main_frame = ttk.Frame(window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        row = 0
        
        ttk.Label(main_frame, text="Название:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(main_frame, width=25)
        name_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Стоимость:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        cost_entry = ttk.Entry(main_frame, width=25)
        cost_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Описание:").grid(row=row, column=0, sticky=tk.W, pady=5)
        desc_entry = tk.Text(main_frame, width=25, height=4)
        desc_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        def save():
            try:
                service_info = {
                    'name': name_entry.get().strip(),
                    'monthly_cost': float(cost_entry.get().strip()),
                    'description': desc_entry.get("1.0", tk.END).strip()
                }
                
                success, msg = self.db.add_service(service_info)
                messagebox.showinfo("Успех" if success else "Ошибка", msg)
                if success:
                    self.load_services()
                    window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте правильность ввода стоимости")
        
        ttk.Button(main_frame, text="Сохранить", command=save, width=15).grid(row=row, column=0, columnspan=2, pady=10)
    
    def edit_service(self):
        selected = self.services_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите услугу")
            return
        
        service_data = self.services_tree.item(selected[0])['values']
        self.open_edit_service_window(service_data)
    
    def delete_service(self):
        selected = self.services_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите услугу")
            return
        
        service_data = self.services_tree.item(selected[0])['values']
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную услугу?"):
            success, msg = self.db.delete_service(service_data[0])
            messagebox.showinfo("Успех" if success else "Ошибка", msg)
            if success:
                self.load_services()
    
    def open_edit_service_window(self, service_data):
        window = tk.Toplevel(self.root)
        window.title("Редактирование услуги")
        window.geometry("400x300")
        window.resizable(False, False)
        
        main_frame = ttk.Frame(window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        row = 0
        
        ttk.Label(main_frame, text="Название:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(main_frame, width=25)
        name_entry.insert(0, service_data[1])
        name_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        monthly_cost = float(service_data[2].split()[0])
        
        ttk.Label(main_frame, text="Стоимость:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        cost_entry = ttk.Entry(main_frame, width=25)
        cost_entry.insert(0, str(monthly_cost))
        cost_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Описание:").grid(row=row, column=0, sticky=tk.W, pady=5)
        desc_entry = tk.Text(main_frame, width=25, height=5)
        desc_entry.grid(row=row, column=1, padx=(10, 0), pady=5)
        row += 1
        
        active_var = tk.BooleanVar(value=service_data[3]=="Да")
        ttk.Checkbutton(main_frame, text="Активна", variable=active_var).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        def save():
            try:
                service_info = {
                    'name': name_entry.get().strip(),
                    'monthly_cost': float(cost_entry.get().strip()),
                    'description': desc_entry.get("1.0", tk.END).strip(),
                    'is_active': active_var.get()
                }
                
                success, msg = self.db.update_service(service_data[0], service_info)
                messagebox.showinfo("Успех" if success else "Ошибка", msg)
                if success:
                    self.load_services()
                    window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте правильность ввода стоимости")
        
        ttk.Button(main_frame, text="Сохранить", command=save, width=15).grid(row=row, column=0, columnspan=2, pady=10)
    
    # ===============================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ОТЧЕТАМИ
    # ===============================================
    
    def generate_selected_report(self):
        """Генерирует выбранный отчет"""
        report_type = self.report_type_var.get()
        
        if report_type == "Финансовый":
            self.show_financial_report()
        elif report_type == "Клиенты":
            self.show_clients_report()
        elif report_type == "Услуги":
            self.show_services_report()
        elif report_type == "Полный":
            self.show_full_report()
        elif report_type == "Тарифы":
            self.show_tariffs_report()
        elif report_type == "Платежи":
            self.show_payments_report()
    
    def format_report_for_display(self, title, content):
        """Форматирует отчет для отображения"""
        # Очищаем предыдущий отчет
        self.report_text.config(state='normal')
        self.report_text.delete(1.0, tk.END)
        
        # Устанавливаем заголовок
        self.report_title_label.config(text=title)
        
        # Вставляем содержимое
        self.report_text.insert(1.0, content)
        
        # Делаем текст только для чтения
        self.report_text.config(state='disabled')
        
        # Сохраняем для экспорта
        self.current_report_text = content
        self.current_report_title = title
    
    def show_financial_report(self):
        """Генерирует и показывает финансовый отчет"""
        try:
            report_data = self.db.get_financial_report()
            
            if not report_data:
                self.format_report_for_display("ФИНАНСОВЫЙ ОТЧЕТ", "Нет данных для отображения\n")
                return
            
            # Форматируем отчет в текстовый вид
            report = "=" * 70 + "\n"
            report += "ФИНАНСОВЫЙ ОТЧЕТ\n"
            report += "=" * 70 + "\n\n"
            
            # Заголовок таблицы
            report += f"{'Период':<12} {'Платежи':<10} {'Сумма':<15} {'Средний':<15}\n"
            report += "-" * 60 + "\n"
            
            total_amount = 0
            total_payments = 0
            
            # Данные таблицы
            for row in report_data:
                period = f"{row['Year']}-{row['Month']:02d}"
                payments = row['PaymentCount']
                amount = float(row['TotalAmount'] or 0)
                avg = float(row['AveragePayment'] or 0)
                
                report += f"{period:<12} {payments:<10} {amount:<15.2f} {avg:<15.2f}\n"
                
                total_amount += amount
                total_payments += payments
            
            # Итоги
            report += "-" * 60 + "\n"
            report += f"ИТОГО: {total_payments} платежей на сумму {total_amount:,.2f} руб.\n"
            report += "=" * 70 + "\n"
            
            # Добавляем дату генерации
            report += f"\nДата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            
            self.format_report_for_display("ФИНАНСОВЫЙ ОТЧЕТ", report)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации финансового отчета: {e}")
    
    def show_clients_report(self):
        """Генерирует и показывает отчет по клиентам"""
        try:
            report_data = self.db.get_clients_report()
            
            if not report_data or len(report_data) == 0:
                self.format_report_for_display("ОТЧЕТ ПО КЛИЕНТАМ", "Нет данных для отображения\n")
                return
            
            # Форматируем отчет в текстовый вид
            report = "=" * 70 + "\n"
            report += "ОТЧЕТ ПО КЛИЕНТАМ\n"
            report += "=" * 70 + "\n\n"
            
            # Безопасное получение общего количества клиентов
            total_clients = 0
            if report_data and len(report_data) > 0:
                total_clients = report_data[0].get('TotalClients', 0)
            
            # Заголовок таблицы
            report += f"{'Статус':<20} {'Количество':<12} {'% от общего':<15}\n"
            report += "-" * 50 + "\n"
            
            active_count = 0
            inactive_count = 0
            
            # Данные таблицы
            for row in report_data:
                status = row.get('Status', 'Неизвестно')
                count = row.get('ClientCount', 0)
                
                # Безопасный расчет процента
                percentage = 0
                if total_clients > 0:
                    percentage = (count / total_clients * 100)
                
                report += f"{status:<20} {count:<12} {percentage:<15.2f}%\n"
                
                if status == 'Активные':
                    active_count = count
                elif status == 'Неактивные':
                    inactive_count = count
            
            # Статистика
            report += "\n" + "=" * 50 + "\n"
            report += "СТАТИСТИКА:\n"
            report += "=" * 50 + "\n"
            report += f"Всего клиентов: {total_clients}\n"
            
            if total_clients > 0:
                active_percent = (active_count / total_clients * 100) if total_clients > 0 else 0
                inactive_percent = (inactive_count / total_clients * 100) if total_clients > 0 else 0
                report += f"Активных: {active_count} ({active_percent:.1f}%)\n"
                report += f"Неактивных: {inactive_count} ({inactive_percent:.1f}%)\n"
            else:
                report += "Активных: 0 (0.0%)\n"
                report += "Неактивных: 0 (0.0%)\n"
                
            report += "=" * 50 + "\n"
            
            # Добавляем дату генерации
            report += f"\nДата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            
            self.format_report_for_display("ОТЧЕТ ПО КЛИЕНТАМ", report)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации отчета по клиентам: {e}")
    
    def show_services_report(self):
        """Генерирует и показывает отчет по услугам"""
        try:
            report_data = self.db.get_services_report()
            
            if not report_data:
                self.format_report_for_display("ОТЧЕТ ПО УСЛУГАМ", "Нет данных для отображения\n")
                return
            
            # Форматируем отчет в текстовый вид
            report = "=" * 70 + "\n"
            report += "ОТЧЕТ ПО УСЛУГАМ\n"
            report += "=" * 70 + "\n\n"
            
            # Заголовок таблицы
            report += f"{'Услуга':<25} {'Подключения':<12} {'Стоимость':<12} {'Доход':<15}\n"
            report += "-" * 70 + "\n"
            
            total_revenue = 0
            total_connections = 0
            
            # Данные таблицы
            for row in report_data:
                service = row['Service'][:24]  # Ограничиваем длину названия
                connections = row['ConnectionCount']
                cost = float(row['Cost'] or 0)
                revenue = float(row['TotalRevenue'] or 0)
                
                report += f"{service:<25} {connections:<12} {cost:<12.2f} {revenue:<15.2f}\n"
                
                total_revenue += revenue
                total_connections += connections
            
            # Итоги
            report += "-" * 70 + "\n"
            report += f"ИТОГО: {total_connections} подключений\n"
            report += f"Общий доход: {total_revenue:,.2f} руб.\n"
            report += "=" * 70 + "\n"
            
            # Добавляем дату генерации
            report += f"\nДата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            
            self.format_report_for_display("ОТЧЕТ ПО УСЛУГАМ", report)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации отчета по услугам: {e}")
    
    def show_full_report(self):
        """Генерирует и показывает полный отчет"""
        try:
            report_data = self.db.get_full_report()
            
            if not report_data:
                self.format_report_for_display("ПОЛНЫЙ ОТЧЕТ", "Нет данных для отображения\n")
                return
            
            stats = report_data.get('stats', {})
            popular_tariffs = report_data.get('popular_tariffs', [])
            payments_stats = report_data.get('payments_stats', [])
            
            # Форматируем отчет в текстовый вид
            report = "=" * 80 + "\n"
            report += "ПОЛНЫЙ ОТЧЕТ ИНТЕРНЕТ-ПРОВАЙДЕРА\n"
            report += f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            report += "=" * 80 + "\n\n"
            
            # 1. Общая статистика
            report += "ОБЩАЯ СТАТИСТИКА:\n"
            report += "-" * 50 + "\n"
            report += f"Всего клиентов: {stats.get('TotalClients', 0)}\n"
            report += f"Активных клиентов: {stats.get('ActiveClients', 0)}\n"
            report += f"Доход за последний месяц: {float(stats.get('TotalRevenue', 0)):,.2f} руб.\n\n"
            
            # 2. Популярные тарифы
            if popular_tariffs:
                report += "ПОПУЛЯРНЫЕ ТАРИФЫ:\n"
                report += "-" * 50 + "\n"
                report += f"{'Тариф':<30} {'Подключения':<12}\n"
                report += "-" * 50 + "\n"
                
                for tariff in popular_tariffs:
                    report += f"{tariff.get('TariffName', '')[:29]:<30} {tariff.get('ConnectionCount', 0):<12}\n"
                
                report += "\n"
            
            # 3. Статистика платежей
            if payments_stats:
                report += "СТАТИСТИКА ПЛАТЕЖЕЙ ЗА ПОСЛЕДНИЕ 6 МЕСЯЦЕВ:\n"
                report += "-" * 50 + "\n"
                report += f"{'Период':<12} {'Платежи':<10} {'Сумма':<15} {'Средний':<15}\n"
                report += "-" * 50 + "\n"
                
                total_amount = 0
                total_payments = 0
                
                for payment in payments_stats:
                    period = payment.get('Period', '')
                    count = payment.get('PaymentCount', 0)
                    amount = float(payment.get('TotalAmount', 0))
                    avg = float(payment.get('AveragePayment', 0))
                    
                    report += f"{period:<12} {count:<10} {amount:<15.2f} {avg:<15.2f}\n"
                    
                    total_amount += amount
                    total_payments += count
                
                report += "-" * 50 + "\n"
                report += f"ИТОГО: {total_payments} платежей на сумму {total_amount:,.2f} руб.\n"
                report += "=" * 80 + "\n"
            
            self.format_report_for_display("ПОЛНЫЙ ОТЧЕТ", report)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации полного отчета: {e}")
    
    def show_tariffs_report(self):
        """Генерирует и показывает отчет по тарифам"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        t.TariffName as Тариф,
                        t.DownloadSpeedMbps as СкоростьЗагрузки,
                        t.UploadSpeedMbps as СкоростьОтдачи,
                        t.MonthlyCost as Стоимость,
                        COUNT(c.ConnectionID) as АктивныхПодключений,
                        COUNT(c.ConnectionID) * t.MonthlyCost as ОбщийДоход
                    FROM TariffPlans t
                    LEFT JOIN Connections c ON t.TariffID = c.TariffID AND c.Status = 'Active'
                    WHERE t.IsActive = 1
                    GROUP BY t.TariffName, t.DownloadSpeedMbps, t.UploadSpeedMbps, t.MonthlyCost
                    ORDER BY ОбщийДоход DESC
                """)
                data = cursor.fetchall()
                
                if not data:
                    self.format_report_for_display("ОТЧЕТ ПО ТАРИФАМ", "Нет данных для отображения\n")
                    return
                
                # Форматируем отчет в текстовый вид
                report = "=" * 80 + "\n"
                report += "ОТЧЕТ ПО ТАРИФНЫМ ПЛАНАМ\n"
                report += "=" * 80 + "\n\n"
                
                # Заголовок таблицы
                report += f"{'Тариф':<20} {'Скорость ↓':<12} {'Скорость ↑':<12} {'Стоимость':<12} {'Подкл.':<8} {'Доход':<15}\n"
                report += "-" * 80 + "\n"
                
                total_revenue = 0
                total_connections = 0
                
                # Данные таблицы
                for row in data:
                    tariff = row['Тариф'][:19]
                    download = row['СкоростьЗагрузки']
                    upload = row['СкоростьОтдачи']
                    cost = float(row['Стоимость'])
                    connections = row['АктивныхПодключений']
                    revenue = float(row['ОбщийДоход'] or 0)
                    
                    report += f"{tariff:<20} {download:<12} {upload:<12} {cost:<12.2f} {connections:<8} {revenue:<15.2f}\n"
                    
                    total_revenue += revenue
                    total_connections += connections
                
                # Итоги
                report += "-" * 80 + "\n"
                report += f"ИТОГО: {total_connections} подключений\n"
                report += f"Общий доход: {total_revenue:,.2f} руб.\n"
                report += "=" * 80 + "\n"
                
                # Добавляем дату генерации
                report += f"\nДата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                
                self.format_report_for_display("ОТЧЕТ ПО ТАРИФАМ", report)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации отчета по тарифам: {e}")
    
    def show_payments_report(self):
        """Генерирует и показывает отчет по платежам"""
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.PaymentID,
                        CONCAT(c.LastName, ' ', LEFT(c.FirstName, 1), '.') as Клиент,
                        p.PaymentDate,
                        p.Amount,
                        p.PaymentMethod,
                        p.Status
                    FROM Payments p
                    JOIN Clients c ON p.ClientID = c.ClientID
                    WHERE p.PaymentDate >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    ORDER BY p.PaymentDate DESC
                    LIMIT 50
                """)
                data = cursor.fetchall()
                
                if not data:
                    self.format_report_for_display("ОТЧЕТ ПО ПЛАТЕЖАМ", "Нет данных для отображения\n")
                    return
                
                # Форматируем отчет в текстовый вид
                report = "=" * 80 + "\n"
                report += "ОТЧЕТ ПО ПЛАТЕЖАМ (ЗА ПОСЛЕДНИЕ 30 ДНЕЙ)\n"
                report += "=" * 80 + "\n\n"
                
                # Заголовок таблицы
                report += f"{'ID':<6} {'Клиент':<20} {'Дата':<12} {'Сумма':<12} {'Метод':<12} {'Статус':<10}\n"
                report += "-" * 80 + "\n"
                
                total_amount = 0
                
                # Данные таблицы
                for row in data:
                    payment_id = row['PaymentID']
                    client = row['Клиент'][:19]
                    
                    # Исправление: безопасное форматирование даты
                    payment_date = row['PaymentDate']
                    if payment_date and hasattr(payment_date, 'strftime'):
                        date = payment_date.strftime('%d.%m.%Y')
                    else:
                        date = str(payment_date)[:10]
                    
                    amount = float(row['Amount'])
                    method = row['PaymentMethod'][:11]
                    status = row['Status'][:9]
                    
                    report += f"{payment_id:<6} {client:<20} {date:<12} {amount:<12.2f} {method:<12} {status:<10}\n"
                    
                    total_amount += amount
                
                # Итоги
                report += "-" * 80 + "\n"
                report += f"ИТОГО: {len(data)} платежей на сумму {total_amount:,.2f} руб.\n"
                report += "=" * 80 + "\n"
                
                # Добавляем дату генерации
                report += f"\nДата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                
                self.format_report_for_display("ОТЧЕТ ПО ПЛАТЕЖАМ", report)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации отчета по платежам: {e}")
    
    def save_report_as_text(self):
        """Сохраняет текущий отчет как текстовый документ (TXT)"""
        if not self.current_report_text:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте отчет")
            return
        
        # Предлагаем выбрать файл для сохранения
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ],
            initialfile=f"{self.current_report_title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if not filename:
            return
        
        try:
            # Создаем полный текст отчета для сохранения
            full_report = "=" * 80 + "\n"
            full_report += f"{self.current_report_title}\n"
            full_report += f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            full_report += "=" * 80 + "\n\n"
            full_report += self.current_report_text
            
            # Сохраняем в файл
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(full_report)
            
            # Показываем подтверждение
            messagebox.showinfo("Успех", 
                              f"Отчет успешно сохранен в файл:\n{filename}\n\n"
                              f"Размер файла: {os.path.getsize(filename)} байт")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчет: {e}")
    
    def clear_report(self):
        """Очищает область отчета"""
        self.format_report_for_display("Выберите тип отчета и нажмите 'Сгенерировать'", "")
    
    def logout(self):
        """Выход из системы"""
        self.root.destroy()
        self.login_window.root.deiconify()

# ===============================================
# Класс для меню клиента
# ===============================================

# ===============================================
# Класс для меню клиента (ПОЛНАЯ ВЕРСИЯ)
# ===============================================

class ClientMenuWindow:
    def __init__(self, login_window, user):
        self.login_window = login_window
        self.db = login_window.db
        self.user = user
        self.client_id = user.get('client_id')
        self.client_info = None
        
        self.root = tk.Toplevel()
        self.root.title(f"Панель клиента - {user['username']}")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Получаем информацию о клиенте
        self.load_client_info()
        
        # Создаем Notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создаем вкладки
        self.create_dashboard_tab()
        self.create_services_tab()
        self.create_payments_tab()
        self.create_profile_tab()

        # Кнопка выхода
        ttk.Button(self.root, text="Выйти", command=self.logout, width=15).pack(pady=10)
        
        # Обработчик смены вкладок
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Загружаем данные для первой вкладки
        self.update_dashboard()
    
    def create_dashboard_tab(self):
        """Создает вкладку с дашбордом"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Главная")
        
        # Заголовок с приветствием
        if self.client_info:
            welcome_text = f"Добро пожаловать, {self.client_info['FirstName']} {self.client_info['LastName']}!"
        else:
            welcome_text = f"Добро пожаловать, {self.user['username']}!"
        
        ttk.Label(dashboard_frame, text=welcome_text, 
                font=("Arial", 16, "bold"), foreground="#2c3e50").pack(pady=20)
        
        # Основной фрейм для виджетов
        main_frame = ttk.Frame(dashboard_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Левая колонка - баланс и подключения
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Виджет баланса
        balance_frame = ttk.LabelFrame(left_frame, text="Ваш баланс", padding="15")
        balance_frame.pack(fill='x', pady=10)
        
        self.balance_label = ttk.Label(balance_frame, 
                                    text="Загрузка...",
                                    font=("Arial", 20, "bold"),
                                    foreground="green")
        self.balance_label.pack(pady=10)
        
        ttk.Button(balance_frame, text="Пополнить баланс", 
                command=self.add_balance, width=20).pack(pady=5)
        
        # Виджет активного подключения
        connection_frame = ttk.LabelFrame(left_frame, text="Активное подключение", padding="15")
        connection_frame.pack(fill='x', pady=10)
        
        self.connection_label = ttk.Label(connection_frame, 
                                        text="Загрузка...",
                                        font=("Arial", 10))
        self.connection_label.pack(pady=10, anchor='w')
        
        # Кнопки для управления подключением
        conn_button_frame = ttk.Frame(connection_frame)
        conn_button_frame.pack(pady=10)
        
        ttk.Button(conn_button_frame, text="Сменить тариф", 
                command=self.change_tariff, width=18).pack(side='left', padx=5)
        ttk.Button(conn_button_frame, text="Приостановить", 
                command=self.suspend_connection, width=18).pack(side='left', padx=5)
        
        # Правая колонка - уведомления и быстрые действия
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Виджет уведомлений
        notifications_frame = ttk.LabelFrame(right_frame, text="Последние уведомления", padding="15")
        notifications_frame.pack(fill='both', expand=True, pady=10)
        
        # Создаем Treeview для уведомлений
        columns = ("date", "title", "read")
        self.notifications_tree = ttk.Treeview(notifications_frame, 
                                            columns=columns, 
                                            show="headings",
                                            height=8)
        
        self.notifications_tree.heading("date", text="Дата")
        self.notifications_tree.heading("title", text="Заголовок")
        self.notifications_tree.heading("read", text="Прочитано")
        
        self.notifications_tree.column("date", width=100)
        self.notifications_tree.column("title", width=200)
        self.notifications_tree.column("read", width=80)
        
        scrollbar = ttk.Scrollbar(notifications_frame, 
                                orient=tk.VERTICAL, 
                                command=self.notifications_tree.yview)
        self.notifications_tree.configure(yscrollcommand=scrollbar.set)
        
        self.notifications_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопка отметить все как прочитанные
        ttk.Button(notifications_frame, text="Отметить все прочитанными",
                command=self.mark_all_notifications_read).pack(pady=5)
        
        # Виджет быстрых действий
        actions_frame = ttk.LabelFrame(right_frame, text="Быстрые действия", padding="15")
        actions_frame.pack(fill='x', pady=10)
        
        # Сетка для кнопок
        buttons_grid = ttk.Frame(actions_frame)
        buttons_grid.pack()
        
        ttk.Button(buttons_grid, text="История платежей", 
                command=self.show_payment_history,
                width=25).grid(row=0, column=0, padx=10, pady=10)
    
    def load_client_info(self):
        """Загружает информацию о клиенте"""
        try:
            if not self.client_id:
                # Пробуем получить ID клиента по имени пользователя
                client_info = self.db.get_client_by_username(self.user['username'])
                if client_info:
                    self.client_id = client_info['ClientID']
                    self.client_info = client_info
            else:
                self.client_info = self.db.get_client_by_username(self.user['username'])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные клиента: {e}")
    
    def create_services_tab(self):
        """Создает вкладку с услугами"""
        services_frame = ttk.Frame(self.notebook)
        self.notebook.add(services_frame, text="Услуги")
        
        # Заголовок
        ttk.Label(services_frame, text="Управление услугами", 
                 font=("Arial", 16, "bold"), foreground="#2c3e50").pack(pady=20)
        
        # Основной фрейм с двумя колонками
        main_frame = ttk.Frame(services_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Левая колонка - текущие услуги
        current_frame = ttk.LabelFrame(main_frame, text="Мои активные услуги", padding="15")
        current_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Заголовок с информацией
        info_label = ttk.Label(current_frame, text="Здесь отображаются ваши подключенные услуги", 
                              font=("Arial", 10))
        info_label.pack(pady=(0, 10))
        
        # Treeview для активных услуг
        columns = ("id", "service", "cost", "activated", "status")
        self.current_services_tree = ttk.Treeview(current_frame, 
                                                 columns=columns, 
                                                 show="headings",
                                                 height=10)
        
        self.current_services_tree.heading("id", text="ID")
        self.current_services_tree.heading("service", text="Услуга")
        self.current_services_tree.heading("cost", text="Стоимость")
        self.current_services_tree.heading("activated", text="Активирована")
        self.current_services_tree.heading("status", text="Статус")
        
        self.current_services_tree.column("id", width=50, stretch=False)
        self.current_services_tree.column("service", width=150)
        self.current_services_tree.column("cost", width=80)
        self.current_services_tree.column("activated", width=100)
        self.current_services_tree.column("status", width=80)
        
        scrollbar1 = ttk.Scrollbar(current_frame, 
                                  orient=tk.VERTICAL, 
                                  command=self.current_services_tree.yview)
        self.current_services_tree.configure(yscrollcommand=scrollbar1.set)
        
        self.current_services_tree.pack(side='left', fill='both', expand=True)
        scrollbar1.pack(side='right', fill='y')
        
        # Кнопки для активных услуг
        current_buttons_frame = ttk.Frame(current_frame)
        current_buttons_frame.pack(pady=10)
        
        ttk.Button(current_buttons_frame, text="Отключить услугу", 
                  command=self.deactivate_service_auto,
                  width=18).pack(side='left', padx=5)
        ttk.Button(current_buttons_frame, text="Обновить", 
                  command=self.load_services_data,
                  width=18).pack(side='left', padx=5)
        
        # Правая колонка - доступные услуги
        available_frame = ttk.LabelFrame(main_frame, text="Доступные услуги", padding="15")
        available_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Заголовок
        ttk.Label(available_frame, text="Вы можете подключить эти услуги:", 
                 font=("Arial", 10)).pack(pady=(0, 10))
        
        # Treeview для доступных услуг
        columns2 = ("id", "service", "cost", "description")
        self.available_services_tree = ttk.Treeview(available_frame, 
                                                   columns=columns2, 
                                                   show="headings",
                                                   height=10)
        
        self.available_services_tree.heading("id", text="ID")
        self.available_services_tree.heading("service", text="Услуга")
        self.available_services_tree.heading("cost", text="Стоимость")
        self.available_services_tree.heading("description", text="Описание")
        
        self.available_services_tree.column("id", width=50, stretch=False)
        self.available_services_tree.column("service", width=150)
        self.available_services_tree.column("cost", width=80)
        self.available_services_tree.column("description", width=200)
        
        scrollbar2 = ttk.Scrollbar(available_frame, 
                                  orient=tk.VERTICAL, 
                                  command=self.available_services_tree.yview)
        self.available_services_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.available_services_tree.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
        # Кнопки для доступных услуг
        available_buttons_frame = ttk.Frame(available_frame)
        available_buttons_frame.pack(pady=10)
        
        ttk.Button(available_buttons_frame, text="Подключить услугу", 
                  command=self.activate_service_auto,
                  width=18).pack(side='left', padx=5)
        ttk.Button(available_buttons_frame, text="Подробнее", 
                  command=self.show_service_details,
                  width=18).pack(side='left', padx=5)
        
        # Статистика услуг
        stats_frame = ttk.LabelFrame(services_frame, text="Статистика услуг", padding="10")
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        self.services_stats_label = ttk.Label(stats_frame, text="")
        self.services_stats_label.pack()
    
    def create_payments_tab(self):
        """Создает вкладку с платежами"""
        payments_frame = ttk.Frame(self.notebook)
        self.notebook.add(payments_frame, text="Платежи")
        
        # Заголовок
        ttk.Label(payments_frame, text="Управление платежами", 
                 font=("Arial", 16, "bold"), foreground="#2c3e50").pack(pady=20)
        
        # Верхняя панель с фильтрами и кнопками
        top_frame = ttk.Frame(payments_frame)
        top_frame.pack(fill='x', padx=20, pady=10)
        
        # Левая часть - фильтры
        filter_frame = ttk.LabelFrame(top_frame, text="Фильтры", padding="10")
        filter_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(filter_frame, text="Период:").pack(side='left', padx=5)
        
        self.payment_period_var = tk.StringVar(value="all")
        period_combo = ttk.Combobox(filter_frame, 
                                   textvariable=self.payment_period_var,
                                   values=["Все время", "За месяц", "За 3 месяца", "За год"],
                                   state="readonly",
                                   width=15)
        period_combo.pack(side='left', padx=5)
        
        # Правая часть - кнопки действий
        action_frame = ttk.Frame(top_frame)
        action_frame.pack(side='right')
        
        ttk.Button(action_frame, text="Пополнить баланс", 
                  command=self.add_balance, width=18).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Экспорт в TXT", 
                  command=self.export_payments_txt, width=18).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Распечатать", 
                  command=self.print_payments, width=18).pack(side='left', padx=5)
        
        # Основная область с таблицей платежей
        table_frame = ttk.Frame(payments_frame)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview для платежей
        columns = ("date", "amount", "method", "period", "status", "description")
        self.payments_tree = ttk.Treeview(table_frame, 
                                         columns=columns, 
                                         show="headings",
                                         height=15)
        
        self.payments_tree.heading("date", text="Дата")
        self.payments_tree.heading("amount", text="Сумма (руб.)")
        self.payments_tree.heading("method", text="Способ оплаты")
        self.payments_tree.heading("period", text="Период")
        self.payments_tree.heading("status", text="Статус")
        self.payments_tree.heading("description", text="Описание")
        
        self.payments_tree.column("date", width=120)
        self.payments_tree.column("amount", width=100)
        self.payments_tree.column("method", width=120)
        self.payments_tree.column("period", width=80)
        self.payments_tree.column("status", width=100)
        self.payments_tree.column("description", width=200)
        
        # Настраиваем теги для цветного отображения статусов
        self.payments_tree.tag_configure('completed', foreground='green')
        self.payments_tree.tag_configure('pending', foreground='orange')
        self.payments_tree.tag_configure('failed', foreground='red')
        
        scrollbar = ttk.Scrollbar(table_frame, 
                                 orient=tk.VERTICAL, 
                                 command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.payments_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Нижняя панель со статистикой
        bottom_frame = ttk.Frame(payments_frame)
        bottom_frame.pack(fill='x', padx=20, pady=10)
        
        # Фрейм статистики
        stats_frame = ttk.LabelFrame(bottom_frame, text="Статистика платежей", padding="10")
        stats_frame.pack(fill='x')
        
        self.payment_stats_label = ttk.Label(stats_frame, text="Загрузка статистики...", font=("Arial", 10))
        self.payment_stats_label.pack()
        
        # Кнопка применения фильтров
        ttk.Button(payments_frame, text="Применить фильтры", 
                  command=self.load_payments_data).pack(pady=10)
    
    def create_profile_tab(self):
        """Создает вкладку с профилем клиента"""
        profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(profile_frame, text="Профиль")
        
        # Заголовок
        ttk.Label(profile_frame, text="Мой профиль", 
                 font=("Arial", 16, "bold"), foreground="#2c3e50").pack(pady=20)
        
        # Основной фрейм с двумя колонками
        main_frame = ttk.Frame(profile_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Левая колонка - информация о профиле
        info_frame = ttk.LabelFrame(main_frame, text="Личная информация", padding="15")
        info_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Создаем текст с информацией
        if self.client_info:
            # Форматируем даты
            def format_date(date_value):
                if date_value and hasattr(date_value, 'strftime'):
                    return date_value.strftime('%d.%m.%Y')
                return str(date_value or 'Не указана')
            
            # Получаем активные подключения
            connections = self.db.get_connections(self.client_id)
            active_connections = sum(1 for c in connections if c['Status'] == 'Active')
            
            info_text = f"""
            ЛИЧНАЯ ИНФОРМАЦИЯ:
            • ФИО: {self.client_info['LastName']} {self.client_info['FirstName']} {self.client_info.get('MiddleName', '')}
            • Дата рождения: {format_date(self.client_info['DateOfBirth'])}
            
            КОНТАКТНАЯ ИНФОРМАЦИЯ:
            • Телефон: {self.client_info['PhoneNumber']}
            • Email: {self.client_info['Email'] or 'Не указан'}
            
            АДРЕСА:
            • Адрес регистрации: {self.client_info['RegistrationAddress']}
            • Фактический адрес: {self.client_info['ActualAddress'] or 'Не указан'}
            
            ПАСПОРТНЫЕ ДАННЫЕ:
            • Серия и номер: {self.client_info['PassportSeries']} {self.client_info['PassportNumber']}
            • Дата выдачи: {format_date(self.client_info['IssueDate'])}
            • Кем выдан: {self.client_info['IssuedBy'] or 'Не указано'}
            
            АККАУНТ:
            • Логин: {self.client_info['Username']}
            • Дата регистрации: {format_date(self.client_info['CreationDate'])}
            • Активных подключений: {active_connections}
            • Персональная скидка: {self.client_info.get('PersonalDiscount', 0)}%
            """
        else:
            info_text = "Не удалось загрузить информацию о профиле"
        
        # Текстовая область с информацией
        text_widget = tk.Text(info_frame, height=25, width=50, wrap='word', font=("Arial", 10))
        text_widget.insert(1.0, info_text)
        text_widget.config(state='disabled')
        text_widget.pack(fill='both', expand=True)
        
        # Правая колонка - управление профилем
        control_frame = ttk.LabelFrame(main_frame, text="Управление профилем", padding="15")
        control_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Кнопки управления
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=20)
        
        # Сетка кнопок (только основные функции)
        ttk.Button(button_frame, text="Редактировать профиль", 
                  command=self.edit_profile, width=25).grid(row=0, column=0, pady=10, padx=10)
        ttk.Button(button_frame, text="Сменить пароль", 
                  command=self.change_password, width=25).grid(row=1, column=0, pady=10, padx=10)
        
        # Статус профиля
        status_frame = ttk.LabelFrame(control_frame, text="Статус профиля", padding="10")
        status_frame.pack(pady=20, fill='x')
        
        if self.client_info:
            status_text = "✓ Активен" if self.client_info['IsActive'] else "✗ Заблокирован"
            status_color = "green" if self.client_info['IsActive'] else "red"
            
            status_label = ttk.Label(status_frame, text=status_text, 
                                    font=("Arial", 12, "bold"), foreground=status_color)
            status_label.pack()
            
            if not self.client_info['IsActive']:
                ttk.Label(status_frame, text="Обратитесь в поддержку", 
                         font=("Arial", 9)).pack(pady=5)
    
    def on_tab_changed(self, event):
        """Обработчик смены вкладки"""
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        
        if current_tab == "Главная":
            self.update_dashboard()
        elif current_tab == "Услуги":
            self.load_services_data()
        elif current_tab == "Платежи":
            self.load_payments_data()
        elif current_tab == "Профиль":
            self.update_profile_info()
    
    # ===============================================
    # ОСНОВНЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С ДАННЫМИ
    # ===============================================
    
    def update_dashboard(self):
        """Обновляет данные на дашборде"""
        if not self.client_id:
            messagebox.showerror("Ошибка", "Не удалось загрузить данные клиента")
            return
            
        try:
            # Получаем информацию для дашборда
            dashboard_info = self.db.get_client_dashboard_info(self.client_id)
            
            if dashboard_info and dashboard_info['client']:
                client_info = dashboard_info['client']
                connection_info = dashboard_info['connection']
                
                # Обновляем баланс
                balance = client_info['Balance'] if client_info['Balance'] else 0
                self.balance_label.config(
                    text=f"{balance:,.2f} руб.",
                    foreground="green" if balance >= 0 else "red"
                )
                
                # Обновляем информацию о подключении
                if connection_info:
                    # Форматируем дату следующего платежа
                    next_payment_date = connection_info['NextPaymentDate']
                    if next_payment_date and hasattr(next_payment_date, 'strftime'):
                        next_payment = next_payment_date.strftime('%d.%m.%Y')
                    else:
                        next_payment = str(next_payment_date)[:10] if next_payment_date else 'Не указана'
                        
                    connection_text = f"""
                    Тариф: {connection_info['TariffName']}
                    Скорость: {connection_info['DownloadSpeedMbps']}/{connection_info['UploadSpeedMbps']} Мбит/с
                    Статус: {connection_info['Status']}
                    Ежемесячный платеж: {connection_info['MonthlyPayment']} руб.
                    Следующий платеж: {next_payment}
                    """
                else:
                    connection_text = "Нет активных подключений"
                
                self.connection_label.config(text=connection_text)
                
                # Загружаем уведомления
                notifications = self.db.get_client_notifications(self.client_id, limit=10)
                
                # Очищаем treeview
                for item in self.notifications_tree.get_children():
                    self.notifications_tree.delete(item)
                
                # Добавляем уведомления
                for notification in notifications:
                    # Форматируем дату
                    created_at = notification['CreatedAt']
                    if created_at and hasattr(created_at, 'strftime'):
                        date_str = created_at.strftime('%d.%m.%Y')
                    else:
                        date_str = str(created_at)[:10]
                        
                    read_status = "Да" if notification['IsRead'] else "Нет"
                    item_id = self.notifications_tree.insert("", "end", values=(
                        date_str,
                        notification['Title'],
                        read_status
                    ))
                    
                    # Помечаем важные уведомления жирным шрифтом
                    if notification.get('IsImportant'):
                        self.notifications_tree.item(item_id, tags=('important',))
                
                # Настраиваем тег для важных уведомлений
                self.notifications_tree.tag_configure('important', font=('Arial', 10, 'bold'))
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить дашборд: {str(e)[:100]}")
    
    def load_services_data(self):
        """Загружает данные об услугах"""
        if not self.client_id:
            return
            
        try:
            # Очищаем treeviews
            for item in self.current_services_tree.get_children():
                self.current_services_tree.delete(item)
            for item in self.available_services_tree.get_children():
                self.available_services_tree.delete(item)
            
            # Активные услуги клиента
            client_services = self.db.get_client_services(self.client_id)
            
            total_monthly_cost = 0
            active_services = 0
            
            for service in client_services:
                # Форматируем дату
                activation_date = service['ActivationDate']
                if activation_date and hasattr(activation_date, 'strftime'):
                    activated = activation_date.strftime('%d.%m.%Y')
                else:
                    activated = str(activation_date)[:10] if activation_date else ''
                    
                status = "Активна" if service['IsActive'] else "Неактивна"
                cost = float(service['MonthlyCost'] or 0)
                
                self.current_services_tree.insert("", "end", values=(
                    service['ClientServiceID'],
                    service['ServiceName'],
                    f"{cost:,.2f} руб.",
                    activated,
                    status
                ))
                
                if service['IsActive']:
                    total_monthly_cost += cost
                    active_services += 1
            
            # Доступные услуги
            available_services = self.db.get_available_services()
            
            for service in available_services:
                # Обрезаем описание если оно слишком длинное
                description = service['Description'][:50] + "..." if service['Description'] and len(service['Description']) > 50 else service['Description'] or ''
                cost = float(service['MonthlyCost'] or 0)
                
                self.available_services_tree.insert("", "end", values=(
                    service['ServiceID'],
                    service['ServiceName'],
                    f"{cost:,.2f} руб.",
                    description
                ))
            
            # Обновляем статистику
            stats_text = f"""
            Статистика услуг:
            • Активных услуг: {active_services}
            • Общая ежемесячная стоимость: {total_monthly_cost:,.2f} руб.
            • Всего доступно услуг: {len(available_services)}
            """
            
            self.services_stats_label.config(text=stats_text)
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить услуги: {str(e)[:100]}")
    
    def load_payments_data(self):
        """Загружает данные о платежах"""
        if not self.client_id:
            return
            
        try:
            # Определяем период фильтрации
            period = self.payment_period_var.get()
            
            # Вычисляем даты для фильтрации
            end_date = datetime.now()
            start_date = None
            
            if period == "За месяц":
                start_date = end_date - timedelta(days=30)
            elif period == "За 3 месяца":
                start_date = end_date - timedelta(days=90)
            elif period == "За год":
                start_date = end_date - timedelta(days=365)
            
            # Получаем платежи
            payments = self.db.get_client_payments_filtered(
                self.client_id, 
                start_date, 
                end_date
            )
            
            # Очищаем treeview
            for item in self.payments_tree.get_children():
                self.payments_tree.delete(item)
            
            # Счетчики для статистики
            total_amount = 0
            completed_payments = 0
            pending_payments = 0
            failed_payments = 0
            
            # Добавляем платежи
            for payment in payments:
                # Форматируем дату
                payment_date = payment['PaymentDate']
                if payment_date and hasattr(payment_date, 'strftime'):
                    date_str = payment_date.strftime('%d.%m.%Y %H:%M')
                else:
                    date_str = str(payment_date)
                    
                # Форматируем период
                payment_period = payment['PaymentPeriod']
                if payment_period and hasattr(payment_period, 'strftime'):
                    period_str = payment_period.strftime('%m.%Y')
                else:
                    period_str = str(payment_period)[:7] if payment_period else ''
                
                # Определяем тег в зависимости от статуса
                tags = ()
                if payment['Status'] == 'Completed':
                    tags = ('completed',)
                    total_amount += payment['Amount']
                    completed_payments += 1
                elif payment['Status'] == 'Pending':
                    tags = ('pending',)
                    pending_payments += 1
                elif payment['Status'] == 'Failed':
                    tags = ('failed',)
                    failed_payments += 1
                
                self.payments_tree.insert("", "end", values=(
                    date_str,
                    f"{payment['Amount']:,.2f}",
                    payment['PaymentMethod'],
                    period_str,
                    payment['Status'],
                    payment['Description'] or ''
                ), tags=tags)
            
            # Получаем общую статистику
            stats = self.db.get_payment_statistics(self.client_id)
            
            if stats:
                total_all_payments = stats['total_payments'] or 0
                total_all_amount = float(stats['total_amount'] or 0)
                avg_payment = float(stats['average_payment'] or 0)
                
                # Форматируем даты
                first_payment = stats['first_payment']
                if first_payment and hasattr(first_payment, 'strftime'):
                    first_payment_str = first_payment.strftime('%d.%m.%Y')
                else:
                    first_payment_str = str(first_payment)[:10] if first_payment else 'Нет'
                    
                last_payment = stats['last_payment']
                if last_payment and hasattr(last_payment, 'strftime'):
                    last_payment_str = last_payment.strftime('%d.%m.%Y')
                else:
                    last_payment_str = str(last_payment)[:10] if last_payment else 'Нет'
                
                stats_text = f"""
                Общая статистика:
                • Всего платежей: {total_all_payments}
                • Общая сумма: {total_all_amount:,.2f} руб.
                • Средний платеж: {avg_payment:,.2f} руб.
                
                Статистика за выбранный период:
                • Показано платежей: {len(payments)}
                • Успешных: {completed_payments}
                • Ожидают обработки: {pending_payments}
                • Неудачных: {failed_payments}
                • Сумма: {total_amount:,.2f} руб.
                """
            else:
                stats_text = f"""
                Статистика за выбранный период:
                • Показано платежей: {len(payments)}
                • Успешных: {completed_payments}
                • Ожидают обработки: {pending_payments}
                • Неудачных: {failed_payments}
                • Сумма: {total_amount:,.2f} руб.
                """
            
            self.payment_stats_label.config(text=stats_text)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить платежи: {str(e)[:100]}")
    
    def update_profile_info(self):
        """Обновляет информацию в профиле"""
        if self.client_info:
            # Здесь можно добавить обновление информации на вкладке профиля
            pass
    
    # ===============================================
    # МЕТОДЫ ДЛЯ ОПЕРАЦИЙ КЛИЕНТА
    # ===============================================
    
    def add_balance(self):
        """Пополнение баланса"""
        if not self.client_id:
            return
            
        # Диалог для ввода суммы
        amount_str = simpledialog.askstring("Пополнение баланса", 
                                          "Введите сумму для пополнения (руб.):")
        
        if not amount_str:
            return
            
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Ошибка", "Сумма должна быть положительной")
                return
            
            # Подтверждение
            confirm = messagebox.askyesno("Подтверждение", 
                                         f"Вы уверены, что хотите пополнить баланс на {amount:,.2f} руб.?")
            
            if not confirm:
                return
                
            # Автоматическая обработка платежа
            success, payment_id = self.db.add_payment(
                self.client_id, 
                amount, 
                "Банковская карта",
                f"Пополнение баланса на {amount:,.2f} руб."
            )
            
            if success:
                messagebox.showinfo("Успех", f"Баланс успешно пополнен на {amount:,.2f} руб.\nID платежа: {payment_id}")
                self.update_dashboard()
                self.load_payments_data()
            else:
                messagebox.showerror("Ошибка", payment_id)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")
    
    def show_payment_history(self):
        """Показывает историю изменений баланса"""
        if not self.client_id:
            return
            
        history_window = tk.Toplevel(self.root)
        history_window.title("История баланса")
        history_window.geometry("700x500")
        
        main_frame = ttk.Frame(history_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="История изменений баланса", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Treeview для истории баланса
        columns = ("date", "old", "new", "change", "type", "description")
        history_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        history_tree.heading("date", text="Дата")
        history_tree.heading("old", text="Было (руб.)")
        history_tree.heading("new", text="Стало (руб.)")
        history_tree.heading("change", text="Изменение")
        history_tree.heading("type", text="Тип")
        history_tree.heading("description", text="Описание")
        
        history_tree.column("date", width=120)
        history_tree.column("old", width=100)
        history_tree.column("new", width=100)
        history_tree.column("change", width=100)
        history_tree.column("type", width=100)
        history_tree.column("description", width=150)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=history_tree.yview)
        history_tree.configure(yscrollcommand=scrollbar.set)
        
        history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        try:
            balance_history = self.db.get_balance_history(self.client_id, limit=50)
            
            for record in balance_history:
                # Форматируем дату
                created_at = record['CreatedAt']
                if created_at and hasattr(created_at, 'strftime'):
                    date_str = created_at.strftime('%d.%m.%Y %H:%M')
                else:
                    date_str = str(created_at)
                    
                change_color = "+" if record['ChangeAmount'] >= 0 else ""
                change_display = f"{change_color}{record['ChangeAmount']:,.2f}"
                
                history_tree.insert("", "end", values=(
                    date_str,
                    f"{record['OldBalance']:,.2f}",
                    f"{record['NewBalance']:,.2f}",
                    change_display,
                    record['ChangeType'],
                    record['Description'] or ''
                ))
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)[:100]}")
    
    def change_tariff(self):
        """Смена тарифного плана"""
        if not self.client_id:
            return
            
        tariff_window = tk.Toplevel(self.root)
        tariff_window.title("Смена тарифного плана")
        tariff_window.geometry("600x500")
        
        main_frame = ttk.Frame(tariff_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Выберите новый тарифный план:", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Получаем текущий тариф
        current_tariff = None
        try:
            connections = self.db.get_connections(self.client_id)
            for conn in connections:
                if conn['Status'] == 'Active':
                    current_tariff = conn['TariffID']
                    break
        except:
            pass
        
        # Treeview с доступными тарифами
        columns = ("id", "name", "download", "upload", "cost", "description")
        tariffs_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)
        
        tariffs_tree.heading("id", text="ID")
        tariffs_tree.heading("name", text="Название")
        tariffs_tree.heading("download", text="Скорость ↓")
        tariffs_tree.heading("upload", text="Скорость ↑")
        tariffs_tree.heading("cost", text="Стоимость")
        tariffs_tree.heading("description", text="Описание")
        
        tariffs_tree.column("id", width=50, stretch=False)
        tariffs_tree.column("name", width=120)
        tariffs_tree.column("download", width=80)
        tariffs_tree.column("upload", width=80)
        tariffs_tree.column("cost", width=80)
        tariffs_tree.column("description", width=150)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tariffs_tree.yview)
        tariffs_tree.configure(yscrollcommand=scrollbar.set)
        
        tariffs_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        try:
            available_tariffs = self.db.get_available_tariffs()
            
            for tariff in available_tariffs:
                description = tariff['Description'][:50] + "..." if tariff['Description'] and len(tariff['Description']) > 50 else tariff['Description'] or ''
                cost = float(tariff['MonthlyCost'] or 0)
                
                item_id = tariffs_tree.insert("", "end", values=(
                    tariff['TariffID'],
                    tariff['TariffName'],
                    f"{tariff['DownloadSpeedMbps']} Мбит/с",
                    f"{tariff['UploadSpeedMbps']} Мбит/с",
                    f"{cost:,.2f} руб.",
                    description
                ))
                
                # Выделяем текущий тариф
                if current_tariff and tariff['TariffID'] == current_tariff:
                    tariffs_tree.item(item_id, tags=('current',))
            
            # Настраиваем тег для текущего тарифа
            tariffs_tree.tag_configure('current', background='lightblue')
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить тарифы: {str(e)[:100]}")
            tariff_window.destroy()
            return
        
        def apply_tariff():
            selected = tariffs_tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Выберите тариф")
                return
                
            tariff_data = tariffs_tree.item(selected[0])['values']
            tariff_id = tariff_data[0]
            tariff_name = tariff_data[1]
            tariff_cost = tariff_data[4]
            
            # Подтверждение
            confirm = messagebox.askyesno("Подтверждение", 
                                         f"Вы уверены, что хотите сменить тариф на '{tariff_name}'?\n"
                                         f"Новая стоимость: {tariff_cost}/мес.")
            
            if not confirm:
                return
            
            # Изменение тарифа
            success, msg = self.db.change_client_tariff(self.client_id, tariff_id)
            
            if success:
                messagebox.showinfo("Успех", f"Тариф успешно изменен на '{tariff_name}'")
                tariff_window.destroy()
                self.update_dashboard()
            else:
                messagebox.showerror("Ошибка", msg)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Применить тариф", 
                  command=apply_tariff, width=20).pack(pady=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=tariff_window.destroy, width=20).pack(pady=5)
    
    def edit_profile(self):
        """Редактирование профиля клиента"""
        if not self.client_info:
            messagebox.showwarning("Ошибка", "Не удалось загрузить информацию о клиенте")
            return
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование профиля")
        edit_window.geometry("500x700")
        edit_window.resizable(False, False)
        
        # Создаем Canvas и Scrollbar
        main_frame = ttk.Frame(edit_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Заголовок
        ttk.Label(scrollable_frame, text="Редактирование профиля", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        row = 1
        
        # Основная информация
        ttk.Label(scrollable_frame, text="Основная информация", 
                 font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        # Имя
        ttk.Label(scrollable_frame, text="Имя:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        first_name_entry = ttk.Entry(scrollable_frame, width=30)
        first_name_entry.insert(0, self.client_info['FirstName'])
        first_name_entry.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Фамилия
        ttk.Label(scrollable_frame, text="Фамилия:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        last_name_entry = ttk.Entry(scrollable_frame, width=30)
        last_name_entry.insert(0, self.client_info['LastName'])
        last_name_entry.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Отчество
        ttk.Label(scrollable_frame, text="Отчество:").grid(row=row, column=0, sticky=tk.W, pady=5)
        middle_name_entry = ttk.Entry(scrollable_frame, width=30)
        middle_name_entry.insert(0, self.client_info.get('MiddleName', ''))
        middle_name_entry.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Дата рождения
        ttk.Label(scrollable_frame, text="Дата рождения:").grid(row=row, column=0, sticky=tk.W, pady=5)
        birth_date_entry = ttk.Entry(scrollable_frame, width=30)
        birth_date = self.client_info['DateOfBirth']
        if birth_date and hasattr(birth_date, 'strftime'):
            birth_date_entry.insert(0, birth_date.strftime('%Y-%m-%d'))
        else:
            birth_date_entry.insert(0, str(birth_date or ''))
        birth_date_entry.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Контактная информация
        ttk.Label(scrollable_frame, text="Контактная информация", 
                 font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        # Телефон
        ttk.Label(scrollable_frame, text="Телефон:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(scrollable_frame, width=30)
        phone_entry.insert(0, self.client_info['PhoneNumber'])
        phone_entry.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Email
        ttk.Label(scrollable_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(scrollable_frame, width=30)
        email_entry.insert(0, self.client_info.get('Email', ''))
        email_entry.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Адреса
        ttk.Label(scrollable_frame, text="Адреса", 
                 font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        # Адрес регистрации
        ttk.Label(scrollable_frame, text="Адрес регистрации:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        reg_address_text = tk.Text(scrollable_frame, width=30, height=3)
        reg_address_text.insert("1.0", self.client_info['RegistrationAddress'])
        reg_address_text.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Фактический адрес
        ttk.Label(scrollable_frame, text="Фактический адрес:").grid(row=row, column=0, sticky=tk.W, pady=5)
        actual_address_text = tk.Text(scrollable_frame, width=30, height=3)
        actual_address_text.insert("1.0", self.client_info.get('ActualAddress', ''))
        actual_address_text.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Паспортные данные
        ttk.Label(scrollable_frame, text="Паспортные данные", 
                 font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        # Серия паспорта
        ttk.Label(scrollable_frame, text="Серия паспорта:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        passport_series_entry = ttk.Entry(scrollable_frame, width=30)
        passport_series_entry.insert(0, self.client_info['PassportSeries'])
        passport_series_entry.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Номер паспорта
        ttk.Label(scrollable_frame, text="Номер паспорта:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        passport_number_entry = ttk.Entry(scrollable_frame, width=30)
        passport_number_entry.insert(0, self.client_info['PassportNumber'])
        passport_number_entry.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Дата выдачи
        ttk.Label(scrollable_frame, text="Дата выдачи:").grid(row=row, column=0, sticky=tk.W, pady=5)
        issue_date_entry = ttk.Entry(scrollable_frame, width=30)
        issue_date = self.client_info['IssueDate']
        if issue_date and hasattr(issue_date, 'strftime'):
            issue_date_entry.insert(0, issue_date.strftime('%Y-%m-%d'))
        else:
            issue_date_entry.insert(0, str(issue_date or ''))
        issue_date_entry.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Кем выдан
        ttk.Label(scrollable_frame, text="Кем выдан:").grid(row=row, column=0, sticky=tk.W, pady=5)
        issued_by_entry = ttk.Entry(scrollable_frame, width=30)
        issued_by_entry.insert(0, self.client_info.get('IssuedBy', ''))
        issued_by_entry.grid(row=row, column=1, padx=(10, 0), pady=5, sticky='w')
        row += 1
        
        # Кнопки
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        def save_profile():
            """Сохранение изменений профиля"""
            try:
                # Собираем данные
                client_data = {
                    'username': self.client_info['Username'],  # Логин не меняем
                    'first_name': first_name_entry.get().strip(),
                    'last_name': last_name_entry.get().strip(),
                    'middle_name': middle_name_entry.get().strip(),
                    'birth_date': birth_date_entry.get().strip() if birth_date_entry.get().strip() else None,
                    'phone': phone_entry.get().strip(),
                    'email': email_entry.get().strip() if email_entry.get().strip() else None,
                    'actual_address': actual_address_text.get("1.0", tk.END).strip(),
                    'reg_address': reg_address_text.get("1.0", tk.END).strip(),
                    'passport_series': passport_series_entry.get().strip(),
                    'passport_number': passport_number_entry.get().strip(),
                    'issue_date': issue_date_entry.get().strip() if issue_date_entry.get().strip() else None,
                    'issued_by': issued_by_entry.get().strip(),
                    'is_active': self.client_info['IsActive']  # Статус не меняем
                }
                
                # Проверка обязательных полей
                required_fields = ['first_name', 'last_name', 'phone', 'reg_address', 
                                 'passport_series', 'passport_number']
                
                for field in required_fields:
                    if not client_data[field]:
                        messagebox.showwarning("Ошибка", f"Поле '{field}' обязательно для заполнения")
                        return
                
                # Подтверждение
                confirm = messagebox.askyesno("Подтверждение", 
                                             "Вы уверены, что хотите сохранить изменения?")
                
                if not confirm:
                    return
                
                # Обновляем данные в базе
                success, msg = self.db.update_client_full(self.client_id, client_data)
                
                if success:
                    # Обновляем локальную информацию
                    self.load_client_info()
                    self.update_dashboard()
                    
                    messagebox.showinfo("Успех", "Профиль успешно обновлен!")
                    edit_window.destroy()
                    
                    # Обновляем вкладку профиля
                    self.update_profile_info()
                else:
                    messagebox.showerror("Ошибка", msg)
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить профиль: {str(e)[:100]}")
        
        def cancel_edit():
            """Отмена редактирования"""
            edit_window.destroy()
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=save_profile, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=cancel_edit, width=15).pack(side=tk.LEFT, padx=5)
        
        # Обязательные поля
        ttk.Label(scrollable_frame, text="* - обязательные поля", 
                 foreground="gray", font=("Arial", 8)).grid(row=row+1, column=0, columnspan=2)
        
        # Размещаем Canvas и Scrollbar
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Фокус на поле имени
        first_name_entry.focus()
    
    def change_password(self):
        """Смена пароля"""
        password_window = tk.Toplevel(self.root)
        password_window.title("Смена пароля")
        password_window.geometry("350x300")
        
        main_frame = ttk.Frame(password_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Смена пароля", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Текущий пароль
        ttk.Label(main_frame, text="Текущий пароль:").pack(anchor='w', pady=(5, 0))
        current_entry = ttk.Entry(main_frame, show="*", width=25)
        current_entry.pack(fill='x', pady=(0, 15))
        
        # Новый пароль
        ttk.Label(main_frame, text="Новый пароль:").pack(anchor='w', pady=(5, 0))
        new_entry = ttk.Entry(main_frame, show="*", width=25)
        new_entry.pack(fill='x', pady=(0, 15))
        
        # Подтверждение пароля
        ttk.Label(main_frame, text="Подтвердите пароль:").pack(anchor='w', pady=(5, 0))
        confirm_entry = ttk.Entry(main_frame, show="*", width=25)
        confirm_entry.pack(fill='x', pady=(0, 20))
        
        def save_password():
            current = current_entry.get()
            new = new_entry.get()
            confirm = confirm_entry.get()
            
            if not current or not new or not confirm:
                messagebox.showwarning("Ошибка", "Заполните все поля")
                return
                
            if new != confirm:
                messagebox.showerror("Ошибка", "Новые пароли не совпадают")
                return
            
            # Проверка сложности пароля
            if len(new) < 6:
                messagebox.showwarning("Ошибка", "Пароль должен содержать минимум 6 символов")
                return
            
            # Подтверждение
            confirm_change = messagebox.askyesno("Подтверждение", 
                                               "Вы уверены, что хотите сменить пароль?")
            
            if not confirm_change:
                return
                
            try:
                success, msg = self.db.change_client_password(
                    self.client_id, current, new
                )
                
                if success:
                    messagebox.showinfo("Успех", "Пароль успешно изменен")
                    password_window.destroy()
                else:
                    messagebox.showerror("Ошибка", msg)
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить пароль: {str(e)[:100]}")
        
        ttk.Button(main_frame, text="Изменить пароль", 
                  command=save_password, width=20).pack(pady=10)
    
    def activate_service_auto(self):
        """Подключение новой услуги"""
        selected = self.available_services_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите услугу для подключения")
            return
            
        service_data = self.available_services_tree.item(selected[0])['values']
        service_id = service_data[0]
        service_name = service_data[1]
        service_cost = service_data[2]
        
        # Подтверждение
        confirm = messagebox.askyesno("Подтверждение", 
                                     f"Вы уверены, что хотите подключить услугу '{service_name}'?\n"
                                     f"Стоимость: {service_cost}/мес.")
        
        if not confirm:
            return
        
        # Автоматическое подключение услуги
        success, msg = self.db.add_client_service(self.client_id, service_id)
        
        if success:
            messagebox.showinfo("Успех", f"Услуга '{service_name}' успешно подключена!")
            self.load_services_data()
            self.update_dashboard()
        else:
            messagebox.showerror("Ошибка", msg)
    
    def deactivate_service_auto(self):
        """Отключение услуги"""
        selected = self.current_services_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите услугу для отключения")
            return
            
        service_data = self.current_services_tree.item(selected[0])['values']
        client_service_id = service_data[0]
        service_name = service_data[1]
        service_status = service_data[4]
        
        if service_status != "Активна":
            messagebox.showwarning("Ошибка", "Можно отключать только активные услуги")
            return
        
        # Подтверждение
        confirm = messagebox.askyesno("Подтверждение", 
                                     f"Вы уверены, что хотите отключить услугу '{service_name}'?")
        
        if not confirm:
            return
        
        # Автоматическое отключение услуги
        success, msg = self.db.remove_client_service(client_service_id)
        
        if success:
            messagebox.showinfo("Успех", f"Услуга '{service_name}' успешно отключена")
            self.load_services_data()
            self.update_dashboard()
        else:
            messagebox.showerror("Ошибка", msg)
    
    def export_payments_txt(self):
        """Экспорт платежей в TXT"""
        if not self.client_id:
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            initialfile=f"payments_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        
        if not filename:
            return
        
        try:
            # Получаем платежи для экспорта
            payments = self.db.get_client_payments(self.client_id, 'all')
            
            # Создаем текстовый отчет
            txt_content = "=" * 80 + "\n"
            txt_content += "ОТЧЕТ ПО ПЛАТЕЖАМ\n"
            
            client = self.db.get_client_by_id(self.client_id)
            if client:
                txt_content += f"Клиент: {client['LastName']} {client['FirstName']}\n"
            
            txt_content += f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            txt_content += "=" * 80 + "\n\n"
            
            # Заголовки
            txt_content += f"{'Дата':<20} {'Сумма':<12} {'Способ оплаты':<15} {'Статус':<12} {'Описание':<30}\n"
            txt_content += "-" * 90 + "\n"
            
            total_amount = 0
            completed_payments = 0
            
            # Данные
            for payment in payments:
                # Форматируем дату
                payment_date = payment['PaymentDate']
                if payment_date and hasattr(payment_date, 'strftime'):
                    date_str = payment_date.strftime('%d.%m.%Y %H:%M')
                else:
                    date_str = str(payment_date)
                
                amount = float(payment['Amount'])
                method = payment['PaymentMethod'][:14]
                status = payment['Status'][:11]
                description = (payment['Description'] or '')[:28]
                
                txt_content += f"{date_str:<20} {amount:<12.2f} {method:<15} {status:<12} {description:<30}\n"
                
                total_amount += amount
                if payment['Status'] == 'Completed':
                    completed_payments += 1
            
            # Итоги
            txt_content += "-" * 90 + "\n"
            txt_content += f"ИТОГО: {len(payments)} платежей\n"
            txt_content += f"Успешных: {completed_payments}\n"
            txt_content += f"Общая сумма: {total_amount:,.2f} руб.\n"
            
            # Сохраняем в файл
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(txt_content)
            
            messagebox.showinfo("Успех", f"Данные экспортированы в файл:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)[:100]}")
    
    def show_service_details(self):
        """Показать детали услуги"""
        selected = self.available_services_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите услугу")
            return
            
        service_data = self.available_services_tree.item(selected[0])['values']
        service_name = service_data[1]
        service_cost = service_data[2]
        service_desc = service_data[3]
        
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Детали услуги: {service_name}")
        details_window.geometry("400x300")
        
        main_frame = ttk.Frame(details_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text=service_name, 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text=f"Стоимость: {service_cost}/мес.", 
                 font=("Arial", 12)).pack(pady=5)
        
        ttk.Label(main_frame, text="Описание:", 
                 font=("Arial", 11)).pack(anchor='w', pady=(10, 5))
        
        text_widget = tk.Text(main_frame, height=8, width=40, wrap='word')
        text_widget.insert(1.0, service_desc)
        text_widget.config(state='disabled')
        text_widget.pack()
    
    def mark_all_notifications_read(self):
        """Отметить все уведомления как прочитанные"""
        if not self.client_id:
            return
            
        confirm = messagebox.askyesno("Подтверждение", 
                                     "Отметить все уведомления как прочитанные?")
        
        if confirm:
            success = self.db.mark_all_notifications_read(self.client_id)
            if success:
                messagebox.showinfo("Успех", "Все уведомления отмечены как прочитанные")
                self.update_dashboard()
    
    def print_payments(self):
        """Печать платежей"""
        messagebox.showinfo("Информация", "Функция печати в разработке")
    
    def suspend_connection(self):
        """Приостановка подключения"""
        if not self.client_id:
            return
            
        confirm = messagebox.askyesno("Подтверждение", 
                                     "Вы уверены, что хотите приостановить подключение?\n"
                                     "Услуги будут временно недоступны.")
        
        if confirm:
            messagebox.showinfo("Информация", "Запрос на приостановку отправлен в техподдержку")
    
    def logout(self):
        """Выход из системы"""
        confirm = messagebox.askyesno("Подтверждение", 
                                     "Вы уверены, что хотите выйти из системы?")
        
        if confirm:
            self.root.destroy()
            self.login_window.root.deiconify()
            
# ===============================================
# Главная функция
# ===============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()