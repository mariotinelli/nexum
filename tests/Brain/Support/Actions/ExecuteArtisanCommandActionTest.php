<?php

declare(strict_types = 1);

use App\Brain\Support\Actions\ExecuteArtisanCommandAction;
use App\Enums\CommandExecutionStatuses;
use App\Models\CommandExecution;
use App\Models\User;
use Illuminate\Support\Facades\Process;

it('executes an allowed artisan command and logs success', function (): void {
    $user = User::factory()->admin()->create();

    $commandExecution = CommandExecution::factory()->create([
        'user_id'      => $user->id,
        'user_name'    => $user->name,
        'command'      => 'php artisan about',
        'command_name' => 'about',
        'status'       => CommandExecutionStatuses::Queued,
        'output'       => null,
        'exit_code'    => null,
        'duration_ms'  => 0,
    ]);

    Process::fake([
        '*' => Process::result(output: 'Application Name: Remsoft', exitCode: 0),
    ]);

    ExecuteArtisanCommandAction::dispatchSync([
        'commandExecutionId' => $commandExecution->id,
    ]);

    $commandExecution->refresh();

    expect($commandExecution->status)->toBe(CommandExecutionStatuses::Success)
        ->and($commandExecution->command_name)->toBe('about')
        ->and($commandExecution->output)->toContain('Application Name: Remsoft');

    expect(CommandExecution::query()->count())->toBe(1);
});

it('marks as error when command is blocked by security rules', function (): void {
    $user = User::factory()->admin()->create();

    $commandExecution = CommandExecution::factory()->create([
        'user_id'      => $user->id,
        'user_name'    => $user->name,
        'command'      => 'php artisan migrate:fresh',
        'command_name' => 'migrate:fresh',
        'status'       => CommandExecutionStatuses::Queued,
        'output'       => null,
        'exit_code'    => null,
        'duration_ms'  => 0,
    ]);

    ExecuteArtisanCommandAction::dispatchSync([
        'commandExecutionId' => $commandExecution->id,
    ]);

    $commandExecution->refresh();

    expect($commandExecution->status)->toBe(CommandExecutionStatuses::Error)
        ->and($commandExecution->output)->toContain('não pode ser executado');
});

it('captures error output when command exits with failure', function (): void {
    $user = User::factory()->admin()->create();

    $commandExecution = CommandExecution::factory()->create([
        'user_id'      => $user->id,
        'user_name'    => $user->name,
        'command'      => 'about',
        'command_name' => 'about',
        'status'       => CommandExecutionStatuses::Queued,
        'output'       => null,
        'exit_code'    => null,
        'duration_ms'  => 0,
    ]);

    Process::fake([
        '*' => Process::result(errorOutput: 'Falha simulada', exitCode: 1),
    ]);

    ExecuteArtisanCommandAction::dispatchSync([
        'commandExecutionId' => $commandExecution->id,
    ]);

    $commandExecution->refresh();

    expect($commandExecution->status)->toBe(CommandExecutionStatuses::Error)
        ->and($commandExecution->output)->toContain('Falha simulada')
        ->and($commandExecution->command)->toBe('php artisan about');
});
