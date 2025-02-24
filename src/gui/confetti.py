from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QBrush
import random

class Confetti:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.size = random.randint(2, 4)  # Уменьшаем размер конфетти
        self.color = QColor(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        self.speed = random.uniform(1, 3)  # Немного замедляем падение
        self.angle = random.uniform(-0.3, 0.3)  # Уменьшаем разброс
        self.rotation = random.uniform(-2, 2)
        self.opacity = 200  # Немного уменьшаем непрозрачность

class ConfettiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.confetti = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_confetti)
        self.frame_count = 0
        self.max_frames = 100  # Уменьшаем длительность анимации

    def start_animation(self):
        self.frame_count = 0
        self.confetti.clear()
        # Создаем больше конфетти, но они меньше
        for _ in range(150):  # Увеличиваем количество
            x = random.randint(0, self.width())
            y = -random.randint(0, 50)  # Начинаем ближе к верху
            self.confetti.append(Confetti(x, y))
        self.timer.start(16)  # ~60 FPS
        self.show()

    def update_confetti(self):
        self.frame_count += 1
        if self.frame_count >= self.max_frames:
            self.timer.stop()
            self.hide()
            return

        # Обновляем положение каждого конфетти
        for conf in self.confetti:
            conf.y += conf.speed
            conf.x += conf.angle
            conf.rotation += 0.1
            if self.frame_count > self.max_frames * 0.7:  # Начинаем затухание
                conf.opacity = max(0, conf.opacity - 5)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for conf in self.confetti:
            painter.save()
            color = conf.color
            color.setAlpha(conf.opacity)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Перемещаем и вращаем
            painter.translate(QPointF(conf.x, conf.y))
            
            # Рисуем только круги
            rect = QRectF(-conf.size/2, -conf.size/2, conf.size, conf.size)
            painter.drawEllipse(rect)
            
            painter.restore() 