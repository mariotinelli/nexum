<?php

declare(strict_types = 1);

use Pest\Rector\Set\PestSetList;
use Rector\Config\RectorConfig;

return RectorConfig::configure()
    ->withPaths([__DIR__ . '/tests'])
    ->withSkip([
        __DIR__ . '/tests/Brain/Chat/Actions/LinkAnonymousChatSessionActionTest.php',
        __DIR__ . '/tests/Feature/Livewire/Customer/CollaboratorsManagement/Collaborators/UpdateTest.php',
    ])
    ->withSets([
        PestSetList::CODING_STYLE,
    ]);
