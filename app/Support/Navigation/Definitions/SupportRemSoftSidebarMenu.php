<?php

declare(strict_types = 1);

namespace App\Support\Navigation\Definitions;

use App\Models\CommandExecution;
use App\Models\SystemErrorAlert;
use App\Support\Navigation\Contracts\DefinesSidebarMenu;
use App\Support\Navigation\SidebarGroup;
use App\Support\Navigation\SidebarItem;
use App\Support\Navigation\SidebarPermission;

final class SupportRemSoftSidebarMenu implements DefinesSidebarMenu
{
    public function groups(): array
    {
        return [
            new SidebarGroup(
                key: 'support',
                label: 'Suporte',
                items: [
                    new SidebarItem(
                        name: 'Comandos',
                        route: 'admin.support.artisan-commands.index',
                        icon: 'command-line',
                        prefix: 'admin.support.artisan-commands',
                        permission: new SidebarPermission('view-any', [CommandExecution::class]),
                    ),
                    new SidebarItem(
                        name: 'Alertas de Erro',
                        route: 'admin.support.system-error-alerts.index',
                        icon: 'solid.exclamation-triangle',
                        prefix: 'admin.support.system-error-alerts',
                        permission: new SidebarPermission('view-any', [SystemErrorAlert::class]),
                    ),
                ],
            ),
        ];
    }
}
