/* Ember Linux make.conf editor page
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef MAKECONFPAGE_H
#define MAKECONFPAGE_H

#include <QWidget>

class QPlainTextEdit;
class QCheckBox;
class QLabel;
class QPushButton;

class MakeConfPage : public QWidget
{
    Q_OBJECT

public:
    explicit MakeConfPage( QWidget* parent = nullptr );

    QString text() const;
    bool worldUpdate() const;
    bool isValid() const;
    QString statusText() const;

    void setTitle( const QString& title );
    void setDescription( const QString& description );
    void setWorldUpdateLabel( const QString& label );

public slots:
    void suggest();
    void resetToSuggested();
    void validateNow();

signals:
    void validityChanged( bool valid );

private:
    QString buildSuggestion() const;
    void setEditorText( const QString& text );
    void updateDiffLabel();

    QLabel* m_heading = nullptr;
    QLabel* m_description = nullptr;
    QPlainTextEdit* m_editor = nullptr;
    QCheckBox* m_world = nullptr;
    QPushButton* m_suggestButton = nullptr;
    QPushButton* m_resetButton = nullptr;
    QPushButton* m_validateButton = nullptr;
    QLabel* m_status = nullptr;
    QLabel* m_diff = nullptr;
    QString m_suggested;
    QString m_lastStatus;
    bool m_valid = false;
};

#endif
