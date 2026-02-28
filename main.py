from PyQt6 import QtWidgets, uic, QtGui, QtCore
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QImage
import cv2
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
class DesignWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(DesignWindow, self).__init__()
        # Charger directement l'interface
        uic.loadUi('design.ui', self)

        # Dictionnaire pour stocker les noms des widgets
        self.widget_names = {}

        # DÉTECTION AUTOMATIQUE DE TOUS LES LABELS
        print("\n=== TOUS LES LABELS DANS L'INTERFACE ===")
        for widget in self.findChildren(QtWidgets.QLabel):
            if widget.objectName():
                name = widget.objectName()
                print(f"Label trouvé: '{name}'")

                # Essayer de deviner le rôle du label
                if 'original' in name.lower():
                    self.widget_names['image_originale'] = name
                elif 'dim' in name.lower() or 'taille' in name.lower() or 'dimension' in name.lower():
                    self.widget_names['dimension'] = name
                elif 'rouge' in name.lower() or 'red' in name.lower():
                    self.widget_names['composante_rouge'] = name
                elif 'vert' in name.lower() or 'green' in name.lower():
                    self.widget_names['composante_verte'] = name
                elif 'bleu' in name.lower() or 'blue' in name.lower():
                    self.widget_names['composante_bleue'] = name
                elif 'color' in name.lower() and 'hist' in name.lower():
                    self.widget_names['label_color_hist'] = name
                elif 'gray' in name.lower() or 'gris' in name.lower():
                    if 'hist' in name.lower():
                        self.widget_names['label_gray_hist'] = name
                    else:
                        self.widget_names['label_gray'] = name

        print("\n=== CORRESPONDANCES TROUVÉES ===")
        for role, name in self.widget_names.items():
            print(f"{role} -> '{name}'")
        print("===================================\n")

        self.image = None
        self.gray_image = None

        # Connexions avec les noms exacts du designer
        self.btn_browse.clicked.connect(self.get_image)
        self.btn_red.clicked.connect(self.showRedChannel)
        self.btn_green.clicked.connect(self.showGreenChannel)
        self.btn_blue.clicked.connect(self.showBlueChannel)
        self.btn_color_hist.clicked.connect(self.show_HistColor)
        self.btn_validate_gray.clicked.connect(self.show_UpdatedImgGray)
        self.btn_gray_hist.clicked.connect(self.show_HistGray)

    def convert_cv_qt(self, cv_image):
        """Convertit une image OpenCV en QPixmap"""
        try:
            if cv_image is None or cv_image.size == 0:
                return QPixmap()

            if len(cv_image.shape) == 2:
                # Image en niveaux de gris
                h, w = cv_image.shape
                bytes_per_line = w
                qt_image = QImage(cv_image.data, w, h, bytes_per_line, QImage.Format.Format_Grayscale8)
            else:
                # Image couleur - BGR -> RGB
                rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            if qt_image.isNull():
                return QPixmap()

            return QPixmap.fromImage(qt_image)

        except Exception as e:
            print(f"Erreur dans convert_cv_qt: {e}")
            return QPixmap()

    def makeFigure(self, role, pixmap):
        """Affiche un pixmap dans le QLabel correspondant au rôle"""
        try:
            # Récupérer le nom réel du widget
            widget_name = self.widget_names.get(role)
            if not widget_name:
                print(f"Rôle '{role}' non assigné à aucun widget")
                return

            # Chercher le label par son nom
            label = self.findChild(QtWidgets.QLabel, widget_name)
            if not label:
                print(f"Label '{widget_name}' non trouvé")
                return

            if pixmap.isNull():
                print(f"Pixmap null pour {role}")
                return

            # Redimensionner et afficher
            scaled = pixmap.scaled(
                label.width(),
                label.height(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            label.setPixmap(scaled)
            print(f"Image affichée dans {widget_name} (rôle: {role})")

        except Exception as e:
            print(f"Erreur dans makeFigure: {e}")

    def get_image(self):
        """Charge une image depuis le disque"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Choisir une image",
                "",
                "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
            )

            if not file_path:
                return

            print(f"Fichier sélectionné: {file_path}")

            # Lire l'image
            self.image = cv2.imread(file_path)

            if self.image is None:
                QMessageBox.warning(self, "Erreur", "Impossible de charger l'image")
                return

            print(f"Image chargée. Dimensions: {self.image.shape}")

            # Convertir et afficher
            pixmap = self.convert_cv_qt(self.image)

            if pixmap.isNull():
                QMessageBox.warning(self, "Erreur", "Impossible de convertir l'image")
                return

            # Afficher dans le label original
            self.makeFigure("image_originale", pixmap)

            # Afficher les dimensions
            self.showDimensions()

        except Exception as e:
            print(f"Erreur dans get_image: {e}")

    def showDimensions(self):
        """Affiche les dimensions de l'image"""
        try:
            if self.image is not None:
                h, w = self.image.shape[:2]
                ch = self.image.shape[2] if len(self.image.shape) == 3 else 1

                # Chercher le label pour les dimensions
                dim_name = self.widget_names.get('dimension')
                if dim_name:
                    dim_label = self.findChild(QtWidgets.QLabel, dim_name)
                    if dim_label:
                        dim_label.setText(f"Hauteur: {h} px\nLargeur: {w} px\nCanaux: {ch}")
                        print(f"Dimensions affichées dans '{dim_name}': {h}x{w}x{ch}")
                    else:
                        print(f"Label '{dim_name}' non trouvé")
                else:
                    print("Aucun label assigné pour les dimensions")

        except Exception as e:
            print(f"Erreur dans showDimensions: {e}")

    def showRedChannel(self):
        """Affiche le canal rouge"""
        try:
            if self.image is not None:
                r = self.image[:, :, 2].copy()
                img = np.zeros_like(self.image)
                img[:, :, 2] = r
                self.makeFigure("composante_rouge", self.convert_cv_qt(img))
        except Exception as e:
            print(f"Erreur dans showRedChannel: {e}")

    def showGreenChannel(self):
        """Affiche le canal vert"""
        try:
            if self.image is not None:
                g = self.image[:, :, 1].copy()
                img = np.zeros_like(self.image)
                img[:, :, 1] = g
                self.makeFigure("composante_verte", self.convert_cv_qt(img))
        except Exception as e:
            print(f"Erreur dans showGreenChannel: {e}")

    def showBlueChannel(self):
        """Affiche le canal bleu"""
        try:
            if self.image is not None:
                b = self.image[:, :, 0].copy()
                img = np.zeros_like(self.image)
                img[:, :, 0] = b
                self.makeFigure("composante_bleue", self.convert_cv_qt(img))
        except Exception as e:
            print(f"Erreur dans showBlueChannel: {e}")

    def show_HistColor(self):
        """Affiche l'histogramme couleur"""
        try:
            if self.image is not None:
                plt.figure(figsize=(8, 4))
                colors = ('b', 'g', 'r')
                for i, color in enumerate(colors):
                    hist = cv2.calcHist([self.image], [i], None, [256], [0, 256])
                    plt.plot(hist, color=color)

                plt.title("Histogramme couleur")
                plt.xlabel("Intensité")
                plt.ylabel("Nombre de pixels")
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                temp_file = "color_hist_temp.png"
                plt.savefig(temp_file, bbox_inches='tight', dpi=100)
                plt.close()

                if os.path.exists(temp_file):
                    pixmap = QPixmap(temp_file)
                    self.makeFigure("label_color_hist", pixmap)
        except Exception as e:
            print(f"Erreur dans show_HistColor: {e}")

    def getContrast(self):
        """Récupère la valeur de contraste"""
        try:
            text = self.edit_contrast.toPlainText().strip()
            return float(text) if text else 1.0
        except:
            return 1.0

    def getBrightness(self):
        """Récupère la valeur de brillance"""
        try:
            text = self.edit_brightness.toPlainText().strip()
            return float(text) if text else 0.0
        except:
            return 0.0

    def show_UpdatedImgGray(self):
        """Affiche l'image en niveaux de gris"""
        try:
            if self.image is not None:
                alpha = self.getContrast()
                beta = self.getBrightness()

                # Convertir en niveaux de gris
                gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
                self.gray_image = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
                self.makeFigure("label_gray", self.convert_cv_qt(self.gray_image))
        except Exception as e:
            print(f"Erreur dans show_UpdatedImgGray: {e}")

    def show_HistGray(self):
        """Affiche l'histogramme en niveaux de gris"""
        try:
            if self.gray_image is not None:
                hist = cv2.calcHist([self.gray_image], [0], None, [256], [0, 256])

                plt.figure(figsize=(8, 4))
                plt.plot(hist, color='black')
                plt.title("Histogramme en niveaux de gris")
                plt.xlabel("Intensité")
                plt.ylabel("Nombre de pixels")
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                temp_file = "gray_hist_temp.png"
                plt.savefig(temp_file, bbox_inches='tight', dpi=100)
                plt.close()

                if os.path.exists(temp_file):
                    pixmap = QPixmap(temp_file)
                    self.makeFigure("label_gray_hist", pixmap)
        except Exception as e:
            print(f"Erreur dans show_HistGray: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DesignWindow()
    window.show()
    sys.exit(app.exec())