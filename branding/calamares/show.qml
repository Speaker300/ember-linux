/* Ember Linux — Calamares slideshow.
 *
 * SPDX-FileCopyrightText: 2026 Ember Linux contributors
 * SPDX-License-Identifier: CC-BY-SA-4.0
 *
 * slideshowAPI 2: Calamares calls onActivate() when the execution page opens
 * and onLeave() when it is done. Text is deliberately concrete: each slide
 * explains what the installer is doing or what happens on first boot.
 */
import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: presentation

    property color ember: "#F26A3D"
    property color amber: "#FFB35C"
    property color teal: "#3FA796"
    property color frost: "#F4F6F8"
    property color ash: "#C3CAD5"

    titleColor: frost
    textColor: ash
    fontFamily: "Inter"

    Rectangle {
        anchors.fill: parent
        color: "#12161C"
        z: -100
    }

    Timer {
        interval: 11000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    Slide {
        title: qsTr("Setting up Ember Linux")
        fontSize: 15
        titleFontSize: 22
        contentWidth: width * 0.55
        content: [
            qsTr("Your disk is being prepared and the Gentoo stage3 is downloading."),
            qsTr("Ember installs the desktop you chose, then sets up networking and the bootloader."),
            qsTr("A typical online install takes 15–40 minutes. Keep the machine plugged in."),
            qsTr("The live desktop stays usable while the install runs.")
        ]

        SlideArt {
            width: Math.min(parent.width * 0.34, 250)
            height: width
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            number: "01"
            label: "INSTALL"
            accent: presentation.ember
        }
    }

    Slide {
        title: qsTr("Gentoo underneath. Ember on top.")
        fontSize: 15
        titleFontSize: 22
        contentWidth: width * 0.55
        content: [
            qsTr("Ember is built from Gentoo's stage3 and Portage, so packages stay close to upstream."),
            qsTr("Binary packages are used where possible to keep downloads and build times down."),
            qsTr("Update later with: sudo emaint sync -a && sudo emerge -uDN @world"),
            qsTr("Your USE flags and make.conf remain yours to edit.")
        ]

        SlideArt {
            width: Math.min(parent.width * 0.34, 250)
            height: width
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            number: "02"
            label: "PORTAGE"
            accent: presentation.amber
        }
    }

    Slide {
        title: qsTr("A desktop that gets out of the way")
        fontSize: 15
        titleFontSize: 22
        contentWidth: width * 0.55
        content: [
            qsTr("Openbox: a small, fast X11 session with tint2, rofi and a curated menu."),
            qsTr("Xfce: the familiar full desktop, with Thunar and a traditional panel."),
            qsTr("KDE Plasma: a complete Qt desktop for people who want all the pieces."),
            qsTr("Server: no display manager, just a clean command line.")
        ]

        SlideArt {
            width: Math.min(parent.width * 0.34, 250)
            height: width
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            number: "03"
            label: "DESKTOP"
            accent: presentation.teal
        }
    }

    Slide {
        title: qsTr("Boot with confidence")
        fontSize: 15
        titleFontSize: 22
        contentWidth: width * 0.55
        content: [
            qsTr("GRUB is installed for BIOS and UEFI systems, with Ember's own boot theme."),
            qsTr("The installed system boots on its own; the live medium is no longer needed."),
            qsTr("Plymouth shows a quiet Ember splash while the kernel and services start."),
            qsTr("If you need the GRUB menu, hold Shift or press Esc during boot.")
        ]

        SlideArt {
            width: Math.min(parent.width * 0.34, 250)
            height: width
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            number: "04"
            label: "BOOT"
            accent: presentation.ember
        }
    }

    Slide {
        title: qsTr("You're almost there")
        fontSize: 15
        titleFontSize: 22
        contentWidth: width * 0.55
        content: [
            qsTr("When the progress bar finishes, review the summary and choose Restart."),
            qsTr("Remove the installation medium before the machine restarts."),
            qsTr("Log in with the account you created. The first boot takes a little longer."),
            qsTr("Open Welcome to Ember on the desktop for updates, apps and help.")
        ]

        SlideArt {
            width: Math.min(parent.width * 0.34, 250)
            height: width
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            number: "05"
            label: "READY"
            accent: presentation.amber
        }
    }

    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 4
        spacing: 7

        Rectangle {
            width: presentation.currentSlide === 0 ? 22 : 6
            height: 6; radius: 3
            color: presentation.currentSlide === 0 ? presentation.ember : "#4A5361"
            Behavior on width { NumberAnimation { duration: 180 } }
        }
        Rectangle {
            width: presentation.currentSlide === 1 ? 22 : 6
            height: 6; radius: 3
            color: presentation.currentSlide === 1 ? presentation.ember : "#4A5361"
            Behavior on width { NumberAnimation { duration: 180 } }
        }
        Rectangle {
            width: presentation.currentSlide === 2 ? 22 : 6
            height: 6; radius: 3
            color: presentation.currentSlide === 2 ? presentation.ember : "#4A5361"
            Behavior on width { NumberAnimation { duration: 180 } }
        }
        Rectangle {
            width: presentation.currentSlide === 3 ? 22 : 6
            height: 6; radius: 3
            color: presentation.currentSlide === 3 ? presentation.ember : "#4A5361"
            Behavior on width { NumberAnimation { duration: 180 } }
        }
        Rectangle {
            width: presentation.currentSlide === 4 ? 22 : 6
            height: 6; radius: 3
            color: presentation.currentSlide === 4 ? presentation.ember : "#4A5361"
            Behavior on width { NumberAnimation { duration: 180 } }
        }
    }

    function onActivate() {
        presentation.currentSlide = 0;
    }

    function onLeave() {
    }
}
