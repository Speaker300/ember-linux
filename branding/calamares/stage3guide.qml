/* Ember Linux — stage3 guidance page.
 *
 * Loaded by the notesqml instance in settings.conf:
 *   qmlSearch: branding
 *   qmlFilename: stage3guide
 *
 * SPDX-FileCopyrightText: 2026 Ember Linux contributors
 * SPDX-License-Identifier: CC-BY-SA-4.0
 */
import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    width: 800
    height: 520

    Rectangle {
        anchors.fill: parent
        color: "#14171C"
        radius: 10

        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 3
            radius: 1.5
            color: "#F26A3D"
            opacity: 0.9
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 30
        spacing: 12

        Text {
            text: qsTr("Choose your foundation")
            font.family: "Inter"
            font.pixelSize: 26
            font.weight: Font.Bold
            color: "#F4F6F8"
            Layout.fillWidth: true
        }

        Text {
            text: qsTr("Ember installs a Gentoo stage3 before it adds a desktop. Pick the base that matches how you plan to use this machine. You can change it later, but starting with the right base avoids a long rebuild.")
            font.family: "Inter"
            font.pixelSize: 13
            color: "#C3CAD5"
            wrapMode: Text.WordWrap
            lineHeight: 1.25
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.maximumHeight: 230
                radius: 9
                color: "#1B2027"
                border.color: "#F26A3D"
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 7

                    RowLayout {
                        spacing: 8
                        Text {
                            text: qsTr("Desktop stage3")
                            font.family: "Inter"
                            font.pixelSize: 17
                            font.weight: Font.DemiBold
                            color: "#F4F6F8"
                        }
                        Rectangle {
                            radius: 3
                            color: "#F26A3D"
                            implicitWidth: badge.implicitWidth + 12
                            implicitHeight: 18
                            Text {
                                id: badge
                                anchors.centerIn: parent
                                text: qsTr("RECOMMENDED")
                                font.family: "Inter"
                                font.pixelSize: 8
                                font.letterSpacing: 1.2
                                color: "#14171C"
                            }
                        }
                        Item { Layout.fillWidth: true }
                    }

                    Text {
                        text: qsTr("Best for Openbox, Xfce and KDE Plasma")
                        font.family: "Inter"
                        font.pixelSize: 11
                        color: "#FFB35C"
                    }

                    Text {
                        text: qsTr("•  The desktop profile is already enabled.\n•  No large profile switch after installation.\n•  Matches the desktop you select on the next page.")
                        font.family: "Inter"
                        font.pixelSize: 12
                        color: "#C3CAD5"
                        lineHeight: 1.35
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: "#2A313B"
                    }

                    Text {
                        text: qsTr("The default choice for a desktop install.")
                        font.family: "Inter"
                        font.pixelSize: 10
                        color: "#FFB35C"
                        opacity: 0.85
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.maximumHeight: 230
                radius: 9
                color: "#1B2027"
                border.color: "#2A313B"
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 7

                    Text {
                        text: qsTr("Minimal stage3")
                        font.family: "Inter"
                        font.pixelSize: 17
                        font.weight: Font.DemiBold
                        color: "#F4F6F8"
                    }

                    Text {
                        text: qsTr("Best for servers and custom builds")
                        font.family: "Inter"
                        font.pixelSize: 11
                        color: "#A6AEBB"
                    }

                    Text {
                        text: qsTr("•  Smaller base system, no desktop profile.\n•  The right choice for a headless server.\n•  Switching to a desktop later triggers a large rebuild.")
                        font.family: "Inter"
                        font.pixelSize: 12
                        color: "#C3CAD5"
                        lineHeight: 1.35
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: "#2A313B"
                    }

                    Text {
                        text: qsTr("For servers, VMs and hand-built systems.")
                        font.family: "Inter"
                        font.pixelSize: 10
                        color: "#A6AEBB"
                        opacity: 0.9
                    }
                }
            }
        }

        Text {
            text: qsTr("Next: choose the exact stage3 tarball, the init system and the desktop.")
            font.family: "Inter"
            font.pixelSize: 11
            color: "#A6AEBB"
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
    }
}
