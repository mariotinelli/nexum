<?php

declare(strict_types = 1);

namespace App\Brain\Support\Actions;

use App\Enums\CommandExecutionStatuses;
use App\Enums\Queues;
use App\Models\CommandExecution;
use Brain\Action;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Queue\Attributes\Queue;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Process;
use Illuminate\Validation\ValidationException;
use Symfony\Component\Process\PhpExecutableFinder;
use Throwable;

/**
 * @property-read int $commandExecutionId
 */
#[Queue(Queues::LongTimeout)]
class ExecuteArtisanCommandAction extends Action implements ShouldQueue
{
    use Queueable;

    public int $tries = 1;

    protected function rules(): array
    {
        return [
            'commandExecutionId' => ['required', 'integer', 'exists:command_executions,id'],
        ];
    }

    public function handle(): self
    {
        $commandExecution = CommandExecution::query()->findOrFail($this->commandExecutionId);

        $commandExecution->update([
            'status'      => CommandExecutionStatuses::InProgress,
            'output'      => null,
            'exit_code'   => null,
            'duration_ms' => 0,
            'executed_at' => now(),
        ]);

        $startedAtNs = hrtime(true);
        $output      = '';

        try {
            $preparedCommand = $this->prepareCommand($commandExecution->command);

            $result = Process::path(base_path())
                ->timeout((int) config('artisan-executor.timeout', 120))
                ->run($preparedCommand['process_arguments'], function (string $type, string $chunk) use (&$output): void {
                    $output .= $chunk;
                });

            if ($output === '') {
                $output = $result->output() . $result->errorOutput();
            }

            $commandExecution->update([
                'command'           => $preparedCommand['display_command'],
                'command_name'      => $preparedCommand['command_name'],
                'command_arguments' => $preparedCommand['arguments'],
                'status'            => $result->successful() ? CommandExecutionStatuses::Success : CommandExecutionStatuses::Error,
                'exit_code'         => $result->exitCode(),
                'output'            => $output,
                'duration_ms'       => (int) round((hrtime(true) - $startedAtNs) / 1_000_000),
            ]);
        } catch (Throwable $exception) {
            $commandExecution->update([
                'status'      => CommandExecutionStatuses::Error,
                'output'      => trim($output . PHP_EOL . $exception->getMessage()),
                'duration_ms' => (int) round((hrtime(true) - $startedAtNs) / 1_000_000),
            ]);
        }

        return $this;
    }

    /**
     * @return array{process_arguments: array<int, string>, display_command: string, command_name: string, arguments: array<int, string>}
     */
    private function prepareCommand(string $inputCommand): array
    {
        $normalizedInput = trim($inputCommand);

        if ($normalizedInput === '') {
            throw ValidationException::withMessages([
                'command' => 'Informe um comando artisan válido.',
            ]);
        }

        $tokens = array_values(array_filter(
            str_getcsv($normalizedInput, ' ', '"', '\\'),
            static fn (?string $token): bool => $token !== null && $token !== ''
        ));

        if (($tokens[0] ?? null) === 'php') {
            array_shift($tokens);
        }

        if (($tokens[0] ?? null) === 'artisan') {
            array_shift($tokens);
        }

        $commandName = array_shift($tokens);

        if (!is_string($commandName)) {
            throw ValidationException::withMessages([
                'command' => 'Informe um comando artisan válido.',
            ]);
        }

        if (!in_array($commandName, $this->availableCommands(), true)) {
            throw ValidationException::withMessages([
                'command' => 'O comando informado não existe neste projeto.',
            ]);
        }

        $this->ensureCommandIsAllowed($commandName);

        $displayArguments = collect($tokens)
            ->map(
                static fn (string $argument): string => preg_match('/\s/', $argument) === 1
                    ? '"' . addcslashes($argument, '"\\') . '"'
                    : $argument
            )
            ->implode(' ');

        return [
            'process_arguments' => [
                $this->phpBinary(),
                'artisan',
                $commandName,
                ...$tokens,
            ],
            'display_command' => trim('php artisan ' . $commandName . ' ' . $displayArguments),
            'command_name'    => $commandName,
            'arguments'       => $tokens,
        ];
    }

    private function ensureCommandIsAllowed(string $commandName): void
    {
        /** @var array<int, string> $blockedCommands */
        $blockedCommands = config('artisan-executor.blocked_commands', []);

        if (in_array($commandName, $blockedCommands, true)) {
            throw ValidationException::withMessages([
                'command' => 'Este comando não pode ser executado por segurança.',
            ]);
        }

        /** @var array<int, string> $allowedCommands */
        $allowedCommands = config('artisan-executor.allowed_commands', []);
        /** @var array<int, string> $allowedPrefixes */
        $allowedPrefixes = config('artisan-executor.allowed_command_prefixes', []);

        if ($allowedCommands === [] && $allowedPrefixes === []) {
            return;
        }

        $commandIsAllowedByPrefix = collect($allowedPrefixes)
            ->contains(static fn (string $prefix): bool => str_starts_with($commandName, $prefix));

        if (!in_array($commandName, $allowedCommands, true) && !$commandIsAllowedByPrefix) {
            throw ValidationException::withMessages([
                'command' => 'Este comando não está na whitelist de execução.',
            ]);
        }
    }

    /**
     * @return array<int, string>
     */
    private function availableCommands(): array
    {
        return collect(Artisan::all())
            ->keys()
            ->filter(static fn (string $command): bool => $command !== '' && !str_starts_with($command, '_'))
            ->values()
            ->all();
    }

    private function phpBinary(): string
    {
        $configuredBinary = config('artisan-executor.php_binary');

        if (is_string($configuredBinary) && trim($configuredBinary) !== '') {
            return trim($configuredBinary);
        }

        $detectedBinary = (new PhpExecutableFinder())->find(false);

        if (is_string($detectedBinary) && trim($detectedBinary) !== '') {
            return $detectedBinary;
        }

        return 'php';
    }
}
