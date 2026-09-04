<?php

declare(strict_types = 1);

namespace App\Models;

use App\Casts\Datetime;
use App\Enums\CommandExecutionStatuses;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Carbon;

/**
 * @property int $id
 * @property ?int $user_id
 * @property string $user_name
 * @property ?string $ip_address
 * @property string $command
 * @property string $command_name
 * @property array<int, string>|null $command_arguments
 * @property CommandExecutionStatuses $status
 * @property ?int $exit_code
 * @property ?string $output
 * @property int $duration_ms
 * @property Carbon $executed_at
 * @property ?Carbon $created_at
 * @property ?Carbon $updated_at
 * @property ?User $user
 */
class CommandExecution extends BaseModel
{
    /** @use HasFactory<\Database\Factories\CommandExecutionFactory> */
    use HasFactory;

    protected function casts(): array
    {
        return [
            'command_arguments' => 'array',
            'status'            => CommandExecutionStatuses::class,
            'executed_at'       => Datetime::class,
        ];
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}
