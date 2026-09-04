<?php

declare(strict_types = 1);

namespace App\Notifications;

use App\Enums\Queues;
use App\Models\User;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;
use Illuminate\Queue\Attributes\Backoff;
use Illuminate\Queue\Attributes\Queue;
use Illuminate\Queue\Attributes\Tries;

#[Queue(Queues::LowPriority)]
#[Tries(3)]
#[Backoff([10, 30, 60, 120])]
class NewPasswordNotification extends Notification implements ShouldQueue
{
    use Queueable;

    public function __construct(public string $token)
    {
    }

    public function via(User $notifiable): array
    {
        return ['mail'];
    }

    public function toMail(User $notifiable): MailMessage
    {
        return (new MailMessage())
            ->subject('Redefinição de senha - ' . config('app.name'))
            ->greeting('Olá ' . $notifiable->name . '!')
            ->line('Recebemos uma solicitação para redefinir sua senha.')
            ->line('Para criar uma nova senha, clique no botão abaixo:')
            ->action(
                'Redefinir minha senha',
                url('new-password/' . $this->token . '?email=' . $notifiable->email)
            )
            ->line('Se você não solicitou a redefinição de senha, ignore este e-mail.')
            ->line('*Este é um e-mail automático, por favor não responda.*')
            ->salutation('Atenciosamente, ' . config('app.name'))
            ->markdown('vendor.notifications.email');
    }
}
