/* Ember Linux make.conf editor
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef MAKECONFVIEWSTEP_H
#define MAKECONFVIEWSTEP_H

#include "DllMacro.h"
#include "utils/PluginFactory.h"
#include "viewpages/ViewStep.h"

#include <QObject>
#include <QVariantMap>

class MakeConfPage;

class PLUGINDLLEXPORT MakeConfViewStep : public Calamares::ViewStep
{
    Q_OBJECT

public:
    explicit MakeConfViewStep( QObject* parent = nullptr );
    ~MakeConfViewStep() override;

    QString prettyName() const override;
    QString prettyStatus() const override;

    QWidget* widget() override;

    bool isNextEnabled() const override;
    bool isBackEnabled() const override;
    bool isAtBeginning() const override;
    bool isAtEnd() const override;

    Calamares::JobList jobs() const override;

    void setConfigurationMap( const QVariantMap& configurationMap ) override;
    void onActivate() override;
    void onLeave() override;

private:
    MakeConfPage* m_page = nullptr;
    QString m_title;
};

CALAMARES_PLUGIN_FACTORY_DECLARATION( MakeConfViewStepFactory )

#endif
