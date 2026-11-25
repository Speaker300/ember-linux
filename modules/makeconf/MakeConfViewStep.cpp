/* Ember Linux make.conf editor
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#include "MakeConfViewStep.h"

#include "MakeConfPage.h"

#include "GlobalStorage.h"
#include "JobQueue.h"
#include "utils/Logger.h"
#include "utils/Variant.h"

#include <QVariant>

CALAMARES_PLUGIN_FACTORY_DEFINITION( MakeConfViewStepFactory, registerPlugin< MakeConfViewStep >(); )

MakeConfViewStep::MakeConfViewStep( QObject* parent )
    : Calamares::ViewStep( parent )
{
    m_title = tr( "Build configuration" );
}

MakeConfViewStep::~MakeConfViewStep() {}

QString
MakeConfViewStep::prettyName() const
{
    return m_title;
}

QString
MakeConfViewStep::prettyStatus() const
{
    if ( !m_page )
    {
        return QString();
    }
    return tr( "Custom build configuration; @world update after install: %1" )
        .arg( m_page->worldUpdate() ? tr( "yes" ) : tr( "no" ) );
}

QWidget*
MakeConfViewStep::widget()
{
    if ( !m_page )
    {
        m_page = new MakeConfPage();
        connect( m_page, &MakeConfPage::validityChanged, this, &Calamares::ViewStep::nextStatusChanged );
    }
    return m_page;
}

bool
MakeConfViewStep::isNextEnabled() const
{
    return m_page ? m_page->isValid() : true;
}

bool
MakeConfViewStep::isBackEnabled() const
{
    return true;
}

bool
MakeConfViewStep::isAtBeginning() const
{
    return true;
}

bool
MakeConfViewStep::isAtEnd() const
{
    return true;
}

Calamares::JobList
MakeConfViewStep::jobs() const
{
    return {};
}

void
MakeConfViewStep::setConfigurationMap( const QVariantMap& configurationMap )
{
    if ( !m_page )
    {
        m_page = new MakeConfPage();
        connect( m_page, &MakeConfPage::validityChanged, this, &Calamares::ViewStep::nextStatusChanged );
    }
    if ( configurationMap.contains( QStringLiteral( "title" ) ) )
    {
        m_title = Calamares::getString( configurationMap, QStringLiteral( "title" ) );
    }
    if ( m_page )
    {
        m_page->setTitle( m_title );
        if ( configurationMap.contains( QStringLiteral( "description" ) ) )
        {
            m_page->setDescription(
                Calamares::getString( configurationMap, QStringLiteral( "description" ) ) );
        }
        if ( configurationMap.contains( QStringLiteral( "worldUpdateLabel" ) ) )
        {
            m_page->setWorldUpdateLabel(
                Calamares::getString( configurationMap, QStringLiteral( "worldUpdateLabel" ) ) );
        }
    }
}

void
MakeConfViewStep::onActivate()
{
    if ( m_page && !m_page->property( "initialized" ).toBool() )
    {
        m_page->setProperty( "initialized", true );
        m_page->suggest();
    }
}

void
MakeConfViewStep::onLeave()
{
    if ( !m_page )
    {
        widget();
    }
    if ( auto* gs = Calamares::JobQueue::instance()->globalStorage() )
    {
        gs->insert( QStringLiteral( "emberMakeConf" ), m_page->text() );
        gs->insert( QStringLiteral( "emberWorldUpdate" ), m_page->worldUpdate() );
        gs->insert( QStringLiteral( "emberMakeConfValid" ), m_page->isValid() );
    }
}
