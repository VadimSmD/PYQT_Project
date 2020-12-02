import sys
import cv2
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QInputDialog, QMainWindow, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
from PIL import ImageEnhance


class NoImageError(Exception):
    pass


class WrongFileError(Exception):
    pass


class NoFileSelectedError(Exception):
    pass


def blur(pic):
    height, width = pic.shape[::2]
    new_height = int(height / 3)
    new_width = int(width / 3)
    if new_width % 2 == 0:
        new_width -= 1
    if new_height % 2 == 0:
        new_height -= 1
    return cv2.GaussianBlur(pic, (new_height, new_width), 0)


def summ_middle(mass):
    count = 0
    for num in mass:
        count += int(num)
    count = count / len(mass)
    return float(count)


class MainClass(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Project_scheme.ui', self)
        self.FaceScan.clicked.connect(self.facescan)
        self.change_features.clicked.connect(self.change_feature_par)
        self.change_censore.clicked.connect(self.change_censore_par)
        self.importPic.clicked.connect(self.import_picture)
        self.save_last_directory.clicked.connect(self.save_last)
        self.turn_right.clicked.connect(self.transpose_l)
        self.turn_left.clicked.connect(self.transpose_r)
        self.red_button.clicked.connect(self.red)
        self.green_button.clicked.connect(self.green)
        self.blue_button.clicked.connect(self.blue)
        self.all_button.clicked.connect(self.all)
        self.blur_button.clicked.connect(self.change_blur_par)
        self.save_new_dir.clicked.connect(self.save_new)
        self.mid_color.clicked.connect(self.middle)
        self.graph_make.clicked.connect(self.graphs)
        self.save_brightness.clicked.connect(self.save_br)
        self.save_color.clicked.connect(self.save_br)
        self.save_contrast.clicked.connect(self.save_br)
        self.save_sharpness.clicked.connect(self.save_br)
        self.set_brightness.clicked.connect(self.enable_brightness)
        self.set_color_balance.clicked.connect(self.enable_balance)
        self.set_difference.clicked.connect(self.enable_contrast)
        self.set_sharpness.clicked.connect(self.enable_sharpness)
        self.amount_of_sharpness.valueChanged.connect(self.filter_enchance_sharpness)
        self.amount_of_difference.valueChanged.connect(self.filter_enchance_contrast)
        self.amount_of_brightness.valueChanged.connect(self.filter_enchance_brightness)
        self.amount_of_color_balance.valueChanged.connect(self.filter_enchance_balance)
        self.main_face_cascade = cv2.CascadeClassifier("Main_Face_Cascade.xml")
        self.secondary_cascade = cv2.CascadeClassifier('Secondary_Features_Cascade.xml')
        self.saving_directory = ''
        self.possible_formats = ['.jpg', '.jpeg', '.bmp', '.raw', '.tiff', '.psd', '.gif']
        self.censore_on = 0
        self.features_on = 0
        self.blur_on = 0
        self.balance_enabled = 0
        self.contrast_enabled = 0
        self.sharpness_enabled = 0
        self.brightness_enabled = 0
        self.features_window_open = 0
        self.Working_Check_Flag = 0
        self.initUI()

    def initUI(self):
        self.pixmap = QPixmap('standart.jpg')
        self.setWindowTitle('Работа с изображением')
        self.picture.setPixmap(self.pixmap)

    def save_last(self):
        name, ok_pressed = QInputDialog.getText(self, "Введите название файла",
                                                "Как будет называться фото?")
        if ok_pressed:
            count_info = open('Photocount.txt', 'r')
            count = count_info.read()
            count_info.close()
            try:
                self.imported_pixmap.save(name + str(count) + '.jpg', 'PNG')
            except AttributeError:
                self.pixmap.save(name + str(count) + '.jpg', 'PNG')
            new_count = str(int(count) + 1)
            file_info = open('Photocount.txt', 'w')
            file_info.write(new_count)
            file_info.close()

    def save_new(self):
        name, ok_pressed = QInputDialog.getText(self, "Введите новую директорию.",
                                                "Куда будет сохраняться файл?")
        main_dir = os.getcwd()
        if ok_pressed:
            count_info = open('Photocount.txt', 'r')
            count = count_info.read()
            count_info.close()
            os.chdir(name)
            file_name, ok_pressed = QInputDialog.getText(self, "Введите название файла",
                                                         "Как будет называться фото?")
            try:
                self.imported_pixmap.save(file_name + str(count) + '.jpg', 'PNG')
            except AttributeError:
                self.pixmap.save(file_name + str(count) + '.jpg', 'PNG')
            new_count = str(int(count) + 1)
            os.chdir(main_dir)
            file_info = open('Photocount.txt', 'w')
            file_info.write(new_count)
            file_info.close()

    def change_censore_par(self):
        cv2.destroyAllWindows()
        self.censore_on = 0
        button_text = self.censore_check.text()
        if button_text == '':
            self.censore_on = 1
            self.censore_check.setText('Установленно')
        else:
            self.censore_on = 0
            self.censore_check.setText('')

    def change_blur_par(self):
        cv2.destroyAllWindows()
        self.blur_on = 0
        button_text = self.blur.text()
        if button_text == '':
            self.blur_on = 1
            self.blur.setText('Установленно')
        else:
            self.blur_on = 0
            self.blur.setText('')

    def change_feature_par(self):
        cv2.destroyAllWindows()
        self.features_on = 0
        button_text = self.secondary_check.text()
        if button_text == '':
            self.features_on = 1
            self.secondary_check.setText('Установленно')
        else:
            self.features_on = 0
            self.secondary_check.setText('')

    def import_picture(self):
        try:
            request_string = 'Картинка (*.jpg);;Все файлы (*)'
            try:
                picture_name = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '', request_string)[0]
                if picture_name == '':
                    raise NoFileSelectedError
                dot_index = picture_name.index('.')
                file_format = picture_name[dot_index:]
                if file_format not in self.possible_formats:
                    raise WrongFileError
                self.imported_pixmap = QPixmap(picture_name)
                if self.imported_pixmap.size().height() > 471:
                    if self.imported_pixmap.size().width() > 671:
                        self.imported_pixmap = self.imported_pixmap.scaled(671, 471)
                self.picture.setPixmap(self.imported_pixmap)
                self.errors.setText('')
            except NoFileSelectedError:
                self.errors.setText('Вы не выбрали файл')
        except WrongFileError:
            self.errors.setText('Выбран неверный формат файла.')
        self.amount_of_sharpness.setValue(100)
        self.amount_of_color_balance.setValue(100)
        self.amount_of_difference.setValue(100)
        self.amount_of_brightness.setValue(100)
        self.sharpness.setText('Текущее значение: 1')
        self.brightness.setText('Текущее значение: 1')
        self.colors.setText('Текущее значение: 1')
        self.contrast.setText('Текущее значение: 1')

    def facescan(self):
        try:
            webcam_img = cv2.VideoCapture(0)
            self.Working_Check_Flag = 0
            while self.Working_Check_Flag == 0:
                if self.censore_on == 1:
                    color_code = 0
                else:
                    color_code = 255
                error_code, image = webcam_img.read()
                try:
                    image_for_features = image.copy()
                except AttributeError:
                    raise NoImageError

                self.errors.setText('')
                if self.features_on == 1:
                    gray_img_copy = cv2.cvtColor(image_for_features, cv2.COLOR_BGR2GRAY)
                faces_coords = self.main_face_cascade.detectMultiScale(image, scaleFactor=1.5, minNeighbors=5,
                                                                       minSize=(5, 5))
                for (x, y, width, height) in faces_coords:
                    cv2.rectangle(image, (x, y), (x + width, y + height), (0, 0, color_code), 4)
                    if self.features_on == 1:
                        gray_face = gray_img_copy[y:y + height, x:x + width]
                        eyes_detected = self.secondary_cascade.detectMultiScale(gray_face)
                        for (ex, ey, ew, eh) in eyes_detected:
                            cv2.rectangle(gray_face, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 1)
                    if self.blur_on == 1:
                        image[y:y + height, x:x + width] = blur(image[y:y + height, x:x + width])
                    elif self.censore_on == 1:
                        face_data = image[y:y + height, x:x + width]
                        for first_i in range(len(face_data)):
                            for second_i in range(len(face_data[0])):
                                face_data[first_i, second_i] = [0, 0, 0]

                cv2.imshow('Face recognition', image)
                if self.features_on == 1:
                    try:
                        cv2.imshow('Face features', gray_face)
                        self.features_window_open = 1
                    except UnboundLocalError:
                        pass
                pressed_key = cv2.waitKey(30) & 0xFF
                if pressed_key == 27:
                    cv2.destroyAllWindows()
                    self.Working_Check_Flag = 1
                elif pressed_key == 32:

                    height, width, channel = image.shape
                    bytesPerLine = 3 * width
                    qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
                    qImg = QPixmap(qImg)
                    self.picture.setPixmap(qImg)
                    self.imported_pixmap = qImg
                    cv2.destroyAllWindows()
                    self.Working_Check_Flag = 1
                    self.amount_of_sharpness.setValue(100)
                    self.amount_of_color_balance.setValue(100)
                    self.amount_of_difference.setValue(100)
                    self.amount_of_brightness.setValue(100)
                    self.sharpness.setText('Текущее значение: 1')
                    self.brightness.setText('Текущее значение: 1')
                    self.colors.setText('Текущее значение: 1')
                    self.contrast.setText('Текущее значение: 1')
        except NoImageError:
            self.errors.setText('Камера не обнаруженна.')

    def transpose_r(self):
        try:
            self.imported_pixmap.save('buffer_image.jpg', 'PNG')
        except AttributeError:
            self.pixmap.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        img = img.transpose(Image.ROTATE_90)
        img.save('buffer_image.jpg')
        pm = QPixmap('buffer_image.jpg')
        os.remove('buffer_image.jpg')
        self.picture.setPixmap(pm)
        self.imported_pixmap = pm

    def transpose_l(self):
        try:
            self.imported_pixmap.save('buffer_image.jpg', 'PNG')
        except AttributeError:
            self.pixmap.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        img = img.transpose(Image.ROTATE_270)
        img.save('buffer_image.jpg')
        pm = QPixmap('buffer_image.jpg')
        os.remove('buffer_image.jpg')
        self.picture.setPixmap(pm)
        self.imported_pixmap = pm

    def red(self):
        try:
            self.imported_pixmap.save('buffer_image.jpg', 'PNG')
        except AttributeError:
            self.pixmap.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        data = img.getdata()
        img1 = [(el[0], 0, 0) for el in data]
        img.putdata(img1)
        img.save('buffer_image.jpg')
        pm = QPixmap('buffer_image.jpg')
        os.remove('buffer_image.jpg')
        self.picture.setPixmap(pm)

    def green(self):
        try:
            self.imported_pixmap.save('buffer_image.jpg', 'PNG')
        except AttributeError:
            self.pixmap.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        data = img.getdata()
        img1 = [(0, el[1], 0) for el in data]
        img.putdata(img1)
        img.save('buffer_image.jpg')
        pm = QPixmap('buffer_image.jpg')
        os.remove('buffer_image.jpg')
        self.picture.setPixmap(pm)

    def blue(self):
        try:
            self.imported_pixmap.save('buffer_image.jpg', 'PNG')
        except AttributeError:
            self.pixmap.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        data = img.getdata()
        img1 = [(0, 0, el[2]) for el in data]
        img.putdata(img1)
        img.save('buffer_image.jpg')
        pm = QPixmap('buffer_image.jpg')
        os.remove('buffer_image.jpg')
        self.picture.setPixmap(pm)

    def all(self):
        try:
            self.picture.setPixmap(self.imported_pixmap)
        except AttributeError:
            self.picture.setPixmap(self.pixmap)

    def middle(self):
        try:
            pic = self.imported_pixmap
        except AttributeError:
            pic = self.pixmap
        pic.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        pixels = img.load()
        width, height = img.size
        main_red = 0
        main_green = 0
        main_blue = 0
        for x in range(width):
            for y in range(height):
                tuple_pix = pixels[x, y]
                main_red += tuple_pix[0]
                main_green += tuple_pix[1]
                main_blue += tuple_pix[2]
        main_red = int(main_red / (x * y))
        main_blue = int(main_blue / (x * y))
        main_green = int(main_green / (x * y))
        color = (main_red, main_green, main_blue)
        image = Image.open('color.PNG')
        width, height = image.size
        mass = []
        for x in range(width):
            for y in range(height):
                mass.append(color)
        image.putdata(mass)
        image.save('color.PNG', 'PNG')
        pixmap = QPixmap('color.PNG')
        self.color.setPixmap(pixmap)
        try:
            os.remove('buffer_image.jpg')
        except FileNotFoundError:
            pass

    def graphs(self):
        try:
            pic = self.imported_pixmap
        except AttributeError:
            pic = self.pixmap
        pic.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        pixels = img.load()
        width, height = img.size
        red = []
        green = []
        blue = []
        pix_count = width * height
        count = [i for i in range(int(pix_count / height))]
        count_b = [i for i in range(int(pix_count / height), int(2 * pix_count / height))]
        count_g = [i for i in range(int(2 * pix_count / height), int(3 * pix_count / height))]
        for x in range(width):
            red_line = []
            green_line = []
            blue_line = []
            for y in range(height):
                pixel = pixels[x, y]
                red_line.append(pixel[0])
                green_line.append(pixel[1])
                blue_line.append(pixel[2])
            red.append(summ_middle(red_line))
            blue.append(summ_middle(blue_line))
            green.append(summ_middle(green_line))
        self.graph.clear()
        self.graph.plot(count, red, pen='r')
        self.graph.plot(count_b, blue, pen='b')
        self.graph.plot(count_g, green, pen='g')
        try:
            os.remove('buffer_image.jpg')
        except FileNotFoundError:
            pass

    def filter_enchance_brightness(self):
        try:
            pic = self.imported_pixmap
        except AttributeError:
            pic = self.pixmap
        pic.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        value = int(self.amount_of_brightness.value()) / 100
        self.brightness.setText('Текущее значение: ' + str(value))
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(value)
        img.save('buffer_image.jpg')
        pm = QPixmap('buffer_image.jpg')
        self.picture.setPixmap(pm)
        self.filtered_pixmap = pm
        try:
            os.remove('buffer_image.jpg')
        except FileNotFoundError:
            pass

    def enable_brightness(self):
        if self.brightness_enabled == 0:
            self.amount_of_brightness.setEnabled(True)
            self.brightness_enabled = 1
        else:
            self.amount_of_brightness.setEnabled(False)
            self.brightness_enabled = 0

    def save_br(self):
        try:
            self.imported_pixmap = self.filtered_pixmap
        except AttributeError:
            pass

    def filter_enchance_balance(self):
        try:
            pic = self.imported_pixmap
        except AttributeError:
            pic = self.pixmap
        pic.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        value = int(self.amount_of_color_balance.value()) / 100
        self.colors.setText('Текущее значение: ' + str(value))
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(value)
        img.save('buffer_image.jpg')
        pm = QPixmap('buffer_image.jpg')
        self.picture.setPixmap(pm)
        self.filtered_pixmap = pm
        try:
            os.remove('buffer_image.jpg')
        except FileNotFoundError:
            pass

    def enable_balance(self):
        if self.balance_enabled == 0:
            self.amount_of_color_balance.setEnabled(True)
            self.balance_enabled = 1
        else:
            self.amount_of_color_balance.setEnabled(False)
            self.balance_enabled = 0

    def filter_enchance_contrast(self):
        try:
            pic = self.imported_pixmap
        except AttributeError:
            pic = self.pixmap
        pic.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        value = int(self.amount_of_difference.value()) / 100
        self.contrast.setText('Текущее значение: ' + str(value))
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(value)
        img.save('buffer_image.jpg')
        pm = QPixmap('buffer_image.jpg')
        self.picture.setPixmap(pm)
        self.filtered_pixmap = pm
        try:
            os.remove('buffer_image.jpg')
        except FileNotFoundError:
            pass

    def enable_contrast(self):
        if self.contrast_enabled == 0:
            self.amount_of_difference.setEnabled(True)
            self.contrast_enabled = 1
        else:
            self.amount_of_difference.setEnabled(False)
            self.contrast_enabled = 0

    def filter_enchance_sharpness(self):
        try:
            pic = self.imported_pixmap
        except AttributeError:
            pic = self.pixmap
        pic.save('buffer_image.jpg', 'PNG')
        img = Image.open('buffer_image.jpg')
        value = int(self.amount_of_sharpness.value()) / 100
        self.sharpness.setText('Текущее значение: ' + str(value))
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(value)
        img.save('buffer_image.jpg')
        pm = QPixmap('buffer_image.jpg')
        self.picture.setPixmap(pm)
        self.filtered_pixmap = pm
        try:
            os.remove('buffer_image.jpg')
        except FileNotFoundError:
            pass

    def enable_sharpness(self):
        if self.sharpness_enabled == 0:
            self.amount_of_sharpness.setEnabled(True)
            self.sharpness_enabled = 1
        else:
            self.amount_of_sharpness.setEnabled(False)
            self.sharpness_enabled = 0


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    event = MainClass()
    event.show()
    sys.exit(app.exec())
