import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Item {
    width: 800
    height: 600
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 36
        spacing: 18
        Label {
            text: "Choose the right stage3"
            font.pointSize: 24
            font.bold: true
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
        Label {
            text: "Desktop stage3 — RECOMMENDED if you want a desktop. It already uses the desktop profile, so the installer does not need a large profile switch and rebuild later."
            font.pointSize: 13
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
        Label {
            text: "Minimal stage3 — NOT RECOMMENDED if you want a full desktop. It is the right choice for a server or a custom minimal system, but switching it to the desktop profile afterwards can trigger a very large rebuild."
            font.pointSize: 13
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
        Label {
            text: "The next page lets you select the exact stage3 tarball and init system."
            font.pointSize: 12
            opacity: 0.8
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
        Item { Layout.fillHeight: true }
    }
}
