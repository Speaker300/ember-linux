/* Ember Linux make.conf editor page
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#include "MakeConfPage.h"

#include "GlobalStorage.h"
#include "JobQueue.h"

#include <QCheckBox>
#include <QFile>
#include <QFontDatabase>
#include <QFormLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QPlainTextEdit>
#include <QProcess>
#include <QPushButton>
#include <QRegularExpression>
#include <QSignalBlocker>
#include <QThread>
#include <QVBoxLayout>

#include <algorithm>

namespace
{
QString
runCommand( const QString& program, const QStringList& args )
{
    QProcess p;
    p.setProcessChannelMode( QProcess::MergedChannels );
    p.start( program, args );
    if ( !p.waitForStarted( 3000 ) )
    {
        return QString();
    }
    if ( !p.waitForFinished( 5000 ) )
    {
        p.kill();
        return QString();
    }
    return QString::fromLocal8Bit( p.readAllStandardOutput() ).trimmed();
}

QString
cpuDescription()
{
    QFile f( QStringLiteral( "/proc/cpuinfo" ) );
    if ( !f.open( QIODevice::ReadOnly ) )
    {
        return QStringLiteral( "Unknown CPU" );
    }
    const QString all = QString::fromLocal8Bit( f.readAll() );
    QRegularExpression modelRe( QStringLiteral( "^model name\\s*:\\s*(.+)$" ),
                                QRegularExpression::MultilineOption );
    auto m = modelRe.match( all );
    if ( m.hasMatch() )
    {
        return m.captured( 1 ).trimmed();
    }
    return QStringLiteral( "Unknown CPU" );
}

QString
cpuFlags()
{
    const QString out = runCommand( QStringLiteral( "cpuid2cpuflags" ), {} );
    const int colon = out.indexOf( QLatin1Char( ':' ) );
    if ( colon >= 0 )
    {
        QStringList flags = out.mid( colon + 1 ).simplified().split( QLatin1Char( ' ' ), Qt::SkipEmptyParts );
        std::sort( flags.begin(), flags.end() );
        return flags.join( QLatin1Char( ' ' ) );
    }

    // Fallback: intersect /proc/cpuinfo flags with the useful CPU_FLAGS_X86 set.
    QFile f( QStringLiteral( "/proc/cpuinfo" ) );
    if ( !f.open( QIODevice::ReadOnly ) )
    {
        return QString();
    }
    const QString all = QString::fromLocal8Bit( f.readAll() );
    QRegularExpression flagsRe( QStringLiteral( "^flags\\s*:\\s*(.+)$" ),
                                QRegularExpression::MultilineOption );
    auto m = flagsRe.match( all );
    if ( !m.hasMatch() )
    {
        return QString();
    }
    const QStringList have = m.captured( 1 ).simplified().split( QLatin1Char( ' ' ), Qt::SkipEmptyParts );
    const QStringList known { QStringLiteral( "aes" ), QStringLiteral( "avx" ), QStringLiteral( "avx2" ),
                              QStringLiteral( "avx512f" ), QStringLiteral( "avx512bw" ),
                              QStringLiteral( "avx512cd" ), QStringLiteral( "avx512dq" ),
                              QStringLiteral( "avx512vl" ), QStringLiteral( "bmi1" ), QStringLiteral( "bmi2" ),
                              QStringLiteral( "f16c" ), QStringLiteral( "fma3" ), QStringLiteral( "fma4" ),
                              QStringLiteral( "mmx" ), QStringLiteral( "mmxext" ), QStringLiteral( "pclmul" ),
                              QStringLiteral( "popcnt" ), QStringLiteral( "rdrand" ), QStringLiteral( "sha" ),
                              QStringLiteral( "sse" ), QStringLiteral( "sse2" ), QStringLiteral( "sse3" ),
                              QStringLiteral( "sse4_1" ), QStringLiteral( "sse4_2" ), QStringLiteral( "ssse3" ),
                              QStringLiteral( "vpclmulqdq" ), QStringLiteral( "xsave" ) };
    QStringList out2;
    for ( const QString& flag : known )
    {
        if ( have.contains( flag ) )
        {
            out2 << flag;
        }
        else if ( flag == QStringLiteral( "fma3" ) && have.contains( QStringLiteral( "fma" ) ) )
        {
            out2 << flag;
        }
    }
    return out2.join( QLatin1Char( ' ' ) );
}

QString
videoCards()
{
    const QString lspci = runCommand( QStringLiteral( "lspci" ), { QStringLiteral( "-nn" ) } );
    const QStringList lines = lspci.split( QLatin1Char( '\n' ), Qt::SkipEmptyParts );
    QStringList gpus;
    for ( const QString& line : lines )
    {
        const QString lower = line.toLower();
        if ( lower.contains( QStringLiteral( "vga compatible controller" ) )
             || lower.contains( QStringLiteral( "3d controller" ) )
             || lower.contains( QStringLiteral( "display controller" ) ) )
        {
            gpus << line;
        }
    }
    const QString all = gpus.join( QLatin1Char( '\n' ) ).toLower();

    if ( all.contains( QStringLiteral( "virtualbox" ) ) )
    {
        return QStringLiteral( "virtualbox" );
    }
    if ( all.contains( QStringLiteral( "vmware" ) ) )
    {
        return QStringLiteral( "vmware" );
    }
    if ( all.contains( QStringLiteral( "virtio" ) ) || all.contains( QStringLiteral( "red hat" ) ) )
    {
        return QStringLiteral( "virgl" );
    }
    if ( all.contains( QStringLiteral( "nvidia" ) ) )
    {
        return QStringLiteral( "nouveau" );
    }
    if ( all.contains( QStringLiteral( "advanced micro devices" ) ) || all.contains( QStringLiteral( "ati" ) )
         || all.contains( QStringLiteral( "amd" ) ) )
    {
        return QStringLiteral( "amdgpu radeonsi" );
    }
    if ( all.contains( QStringLiteral( "intel" ) ) )
    {
        return QStringLiteral( "intel" );
    }
    return QStringLiteral( "fbdev vesa" );
}

QString
desktopChoice()
{
    if ( auto* gs = Calamares::JobQueue::instance()->globalStorage() )
    {
        const QString v = gs->value( QStringLiteral( "packagechooser_desktopchoose" ) ).toString();
        if ( !v.isEmpty() )
        {
            return v;
        }
    }
    return QStringLiteral( "openbox" );
}

QString
localeName()
{
    QString loc;
    if ( auto* gs = Calamares::JobQueue::instance()->globalStorage() )
    {
        loc = gs->value( QStringLiteral( "locale" ) ).toString();
    }
    if ( loc.isEmpty() )
    {
        loc = QStringLiteral( "en_US.UTF-8" );
    }
    QString lang = loc.section( QLatin1Char( '.' ), 0, 0 ).section( QLatin1Char( '_' ), 0, 0 );
    if ( lang.isEmpty() )
    {
        lang = QStringLiteral( "en" );
    }
    return lang;
}

bool
isEfi()
{
    return QFile::exists( QStringLiteral( "/sys/firmware/efi" ) );
}
}  // namespace

MakeConfPage::MakeConfPage( QWidget* parent )
    : QWidget( parent )
{
    auto* layout = new QVBoxLayout( this );
    layout->setContentsMargins( 0, 0, 0, 0 );

    m_heading = new QLabel( tr( "Build configuration" ), this );
    QFont headingFont = m_heading->font();
    headingFont.setPointSize( headingFont.pointSize() + 6 );
    headingFont.setBold( true );
    m_heading->setFont( headingFont );
    layout->addWidget( m_heading );

    m_description = new QLabel( this );
    m_description->setWordWrap( true );
    layout->addWidget( m_description );

    m_editor = new QPlainTextEdit( this );
    m_editor->setFont( QFontDatabase::systemFont( QFontDatabase::FixedFont ) );
    m_editor->setLineWrapMode( QPlainTextEdit::NoWrap );
    m_editor->setMinimumHeight( 300 );
    layout->addWidget( m_editor, 1 );

    auto* buttons = new QHBoxLayout();
    m_suggestButton = new QPushButton( tr( "&Suggest from hardware" ), this );
    m_resetButton = new QPushButton( tr( "&Reset" ), this );
    m_validateButton = new QPushButton( tr( "&Validate" ), this );
    buttons->addWidget( m_suggestButton );
    buttons->addWidget( m_resetButton );
    buttons->addWidget( m_validateButton );
    buttons->addStretch();
    m_diff = new QLabel( this );
    buttons->addWidget( m_diff );
    layout->addLayout( buttons );

    m_world = new QCheckBox( tr( "Update @world after installation (slower, but keeps the system current)" ), this );
    m_world->setChecked( false );
    layout->addWidget( m_world );

    m_status = new QLabel( this );
    m_status->setWordWrap( true );
    layout->addWidget( m_status );

    connect( m_suggestButton, &QPushButton::clicked, this, &MakeConfPage::suggest );
    connect( m_resetButton, &QPushButton::clicked, this, &MakeConfPage::resetToSuggested );
    connect( m_validateButton, &QPushButton::clicked, this, &MakeConfPage::validateNow );
    connect( m_editor, &QPlainTextEdit::textChanged, this, [this]() {
        updateDiffLabel();
        validateNow();
    } );

    m_suggested = buildSuggestion();
    setEditorText( m_suggested );
}

QString
MakeConfPage::buildSuggestion() const
{
    const int jobs = std::max( 1, QThread::idealThreadCount() );
    const QString desktop = desktopChoice();
    const QString flags = cpuFlags();
    const bool server = desktop == QStringLiteral( "server" );

    QString use;
    if ( server )
    {
        use = QStringLiteral( "-X -wayland dbus elogind" );
    }
    else
    {
        use = QStringLiteral( "X gtk dbus elogind policykit udisks" );
        if ( desktop == QStringLiteral( "kde" ) )
        {
            use += QStringLiteral( " qt6" );
        }
    }

    QString text;
    text += QStringLiteral( "# Ember Linux build configuration\n" );
    text += QStringLiteral( "# Suggested for this machine (%1)\n" ).arg( cpuDescription() );
    text += QStringLiteral( "# Desktop profile: %1\n\n" ).arg( desktop );

    text += QStringLiteral( "COMMON_FLAGS=\"-O2 -pipe -march=native -mtune=native\"\n" );
    text += QStringLiteral( "CFLAGS=\"${COMMON_FLAGS}\"\n" );
    text += QStringLiteral( "CXXFLAGS=\"${COMMON_FLAGS}\"\n" );
    text += QStringLiteral( "FCFLAGS=\"${COMMON_FLAGS}\"\n" );
    text += QStringLiteral( "FFLAGS=\"${COMMON_FLAGS}\"\n\n" );

    text += QStringLiteral( "MAKEOPTS=\"-j%1 -l%2\"\n" ).arg( jobs ).arg( jobs * 2 );
    text += QStringLiteral( "USE=\"%1\"\n" ).arg( use );
    text += QStringLiteral( "VIDEO_CARDS=\"%1\"\n" ).arg( videoCards() );
    text += QStringLiteral( "INPUT_DEVICES=\"libinput\"\n" );
    text += QStringLiteral( "ACCEPT_LICENSE=\"*\"\n" );
    text += QStringLiteral( "GENTOO_MIRRORS=\"https://distfiles.gentoo.org https://gentoo.osuosl.org\"\n" );
    text += QStringLiteral( "FEATURES=\"getbinpkg\"\n" );
    text += QStringLiteral( "BINPKG_COMPRESS=\"zstd\"\n" );
    text += QStringLiteral( "EMERGE_DEFAULT_OPTS=\"--getbinpkg --jobs=%1 --load-average=%2\"\n" )
                .arg( std::min( jobs, 8 ) )
                .arg( jobs * 2 );
    text += QStringLiteral( "GRUB_PLATFORMS=\"efi-64 pc\"\n" );
    if ( !flags.isEmpty() )
    {
        text += QStringLiteral( "CPU_FLAGS_X86=\"%1\"\n" ).arg( flags );
    }
    text += QStringLiteral( "LINGUAS=\"%1\"\n" ).arg( localeName() );
    text += QStringLiteral( "LC_MESSAGES=C.UTF-8\n" );
    text += QStringLiteral( "# Firmware: %1\n" ).arg( isEfi() ? QStringLiteral( "UEFI" ) : QStringLiteral( "BIOS" ) );
    return text;
}

QString
MakeConfPage::text() const
{
    return m_editor->toPlainText();
}

bool
MakeConfPage::worldUpdate() const
{
    return m_world->isChecked();
}

bool
MakeConfPage::isValid() const
{
    return m_valid;
}

QString
MakeConfPage::statusText() const
{
    return m_lastStatus;
}

void
MakeConfPage::setTitle( const QString& title )
{
    m_heading->setText( title );
}

void
MakeConfPage::setDescription( const QString& description )
{
    m_description->setText( description );
}

void
MakeConfPage::setWorldUpdateLabel( const QString& label )
{
    m_world->setText( label );
}

void
MakeConfPage::setEditorText( const QString& text )
{
    const QSignalBlocker blocker( m_editor );
    m_editor->setPlainText( text );
    updateDiffLabel();
    validateNow();
}

void
MakeConfPage::suggest()
{
    m_suggested = buildSuggestion();
    setEditorText( m_suggested );
}

void
MakeConfPage::resetToSuggested()
{
    setEditorText( m_suggested );
}

void
MakeConfPage::updateDiffLabel()
{
    if ( !m_diff )
    {
        return;
    }
    if ( m_editor->toPlainText() == m_suggested )
    {
        m_diff->setText( tr( "Using suggested values" ) );
        return;
    }
    const QStringList a = m_suggested.split( QLatin1Char( '\n' ) );
    const QStringList b = m_editor->toPlainText().split( QLatin1Char( '\n' ) );
    int changed = 0;
    const int n = std::max( a.size(), b.size() );
    for ( int i = 0; i < n; ++i )
    {
        if ( a.value( i ) != b.value( i ) )
        {
            ++changed;
        }
    }
    m_diff->setText( tr( "Edited: %1 line(s) differ" ).arg( changed ) );
}

void
MakeConfPage::validateNow()
{
    const QString text = m_editor->toPlainText();
    QStringList errors;
    QStringList vars;
    const QStringList lines = text.split( QLatin1Char( '\n' ) );
    QRegularExpression assignRe( QStringLiteral( "^([A-Za-z_][A-Za-z0-9_]*)=(.*)$" ) );
    int lineno = 0;
    for ( const QString& raw : lines )
    {
        ++lineno;
        const QString line = raw.trimmed();
        if ( line.isEmpty() || line.startsWith( QLatin1Char( '#' ) ) )
        {
            continue;
        }
        auto m = assignRe.match( line );
        if ( !m.hasMatch() )
        {
            errors << tr( "Line %1: not a KEY=value assignment" ).arg( lineno );
            continue;
        }
        const QString key = m.captured( 1 );
        QString value = m.captured( 2 ).trimmed();
        vars << key;
        if ( value.startsWith( QLatin1Char( '"' ) ) || value.endsWith( QLatin1Char( '"' ) ) )
        {
            if ( value.size() < 2 || !value.startsWith( QLatin1Char( '"' ) )
                 || !value.endsWith( QLatin1Char( '"' ) ) )
            {
                errors << tr( "Line %1: unbalanced quotes" ).arg( lineno );
            }
        }
        if ( value.isEmpty() && key != QStringLiteral( "USE" ) )
        {
            errors << tr( "Line %1: empty value for %2" ).arg( lineno ).arg( key );
        }
        if ( key == QStringLiteral( "MAKEOPTS" ) && !value.contains( QStringLiteral( "-j" ) ) )
        {
            errors << tr( "MAKEOPTS should contain -j" );
        }
    }

    for ( const QString& required : { QStringLiteral( "CFLAGS" ), QStringLiteral( "CXXFLAGS" ),
                                      QStringLiteral( "MAKEOPTS" ), QStringLiteral( "ACCEPT_LICENSE" ) } )
    {
        if ( !vars.contains( required ) )
        {
            errors << tr( "Missing %1" ).arg( required );
        }
    }

    if ( errors.isEmpty() )
    {
        m_valid = true;
        m_lastStatus = tr( "Configuration is valid (%1 variables)." ).arg( vars.size() );
        m_status->setStyleSheet( QStringLiteral( "color: #1b5e20;" ) );
    }
    else
    {
        m_valid = false;
        m_lastStatus = errors.join( QStringLiteral( "; ") );
        m_status->setStyleSheet( QStringLiteral( "color: #b71c1c;" ) );
    }
    m_status->setText( m_lastStatus );
    emit validityChanged( m_valid );
}
