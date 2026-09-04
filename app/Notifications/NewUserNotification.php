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
class NewUserNotification extends Notification implements ShouldQueue
{
    use Queueable;

    public function __construct(public string $password)
    {
    }

    public function via(User $notifiable): array
    {
        return ['mail'];
    }

    public function toMail(User $notifiable): MailMessage
    {
        $mail = (new MailMessage())
            ->subject('Nova conta cadastrada no sistema ' . config('app.name'))
            ->greeting('Olá ' . $notifiable->name . '!')
            ->line('Uma nova conta foi criada para você em nosso sistema!');

        if ($notifiable->type->canAccessAdminArea()) {
            $mail
                ->line('Seu login é: **' . $notifiable->email . '**, e a senha gerada para esta conta é: **' . $this->password . '**')
                ->line('Recomendamos que troque sua senha, para isso clique no menu no canto superior direto, e clique em **Meu Perfil**.')
                ->action('Clique aqui para acessar nosso sistema', route('admin.login'));
        }

        return $mail
            ->line('*Este é um email automático, por favor não responda*')
            ->salutation('Atenciosamente')
            ->markdown('vendor.notifications.email');
    }
}
