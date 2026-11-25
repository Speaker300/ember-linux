import QtQuick 2.15

/* Ember slideshow art card.
 * Kept deliberately geometric so it stays crisp at every scale and needs no
 * external illustrations beyond the Ember mark.
 */
Item {
    id: root

    property string number: "01"
    property string label: "INSTALL"
    property color accent: "#F26A3D"

    Rectangle {
        anchors.fill: parent
        radius: 22
        color: "#141920"
        border.color: "#2A313B"
        border.width: 1
    }

    Rectangle {
        width: parent.width * 0.64
        height: width
        radius: width / 2
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -8
        color: "transparent"
        border.color: root.accent
        border.width: 1.4
        opacity: 0.55
    }

    Rectangle {
        width: parent.width * 0.48
        height: width
        radius: width / 2
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -8
        color: root.accent
        opacity: 0.055
    }

    Text {
        text: root.number
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -10
        font.family: "Inter"
        font.pixelSize: Math.round(root.width * 0.34)
        font.weight: Font.Bold
        color: root.accent
        opacity: 0.95
    }

    Rectangle {
        width: 28
        height: 1
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: label.top
        anchors.bottomMargin: 10
        color: root.accent
        opacity: 0.55
    }

    Text {
        id: label
        text: root.label
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        font.family: "Inter"
        font.pixelSize: 9
        font.letterSpacing: 3
        color: "#A6AEBB"
    }

    Image {
        source: "ember-mark.png"
        width: 22
        height: 22
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 18
        opacity: 0.8
        fillMode: Image.PreserveAspectFit
    }
}
