<?php

declare(strict_types = 1);

namespace App\Jobs;

use App\Enums\Queues;
use App\Support\Alerts\DiscordAlert;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\Attributes\Backoff;
use Illuminate\Queue\Attributes\Queue;
use Illuminate\Queue\Attributes\Tries;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;
use Throwable;

#[Queue(Queues::HighPriority)]
#[Tries(3)]
#[Backoff([10, 30, 60])]
class SendDiscordCriticalAlertJob implements ShouldQueue
{
    use Dispatchable;
    use InteractsWithQueue;
    use Queueable;
    use SerializesModels;

    /**
     * @param  array<string, mixed>  $payload
     */
    public function __construct(public array $payload)
    {
    }

    public function handle(DiscordAlert $discordAlert): void
    {
        try {
            $discordAlert->send($this->payload);
        } catch (Throwable $throwable) {
            Log::warning('Falha ao enviar alerta crítico para o Discord.', [
                'exception' => $throwable::class,
                'message'   => $throwable->getMessage(),
            ]);
        }
    }
}
