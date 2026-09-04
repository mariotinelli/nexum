<?php

declare(strict_types = 1);

use App\Enums\Queues;
use App\Enums\TypeUsers;
use App\Models\User;
use App\Notifications\NewUserNotification;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Queue\Attributes\Queue as QueueAttribute;

it('defines mail channel and queue for new user notification', function (): void {
    $notification   = new NewUserNotification('secret-123');
    $reflection     = new ReflectionClass($notification);
    $queueAttribute = $reflection->getAttributes(QueueAttribute::class);
    $queue          = ($queueAttribute[0] ?? null)?->newInstance();

    expect($queue?->queue)->toBe(Queues::LowPriority->value)
        ->and($notification->via(new User()))->toBe(['mail']);
});

it('builds new user mail message', function (): void {
    $user = User::factory()->make([
        'name'  => 'Maria',
        'email' => 'maria@example.com',
        'type'  => TypeUsers::User,
    ]);

    $mail = (new NewUserNotification('secret-123'))->toMail($user);

    expect($mail)->toBeInstanceOf(MailMessage::class)
        ->and($mail->subject)->toContain('Nova conta cadastrada no sistema')
        ->and($mail->actionText)->toBe('Clique aqui para acessar nosso sistema')
        ->and($mail->actionUrl)->toContain('/admin/login')
        ->and(implode(' ', $mail->introLines))->toContain('secret-123');
});

it('does not expose credentials or an admin link to customers', function (): void {
    $customer = User::factory()->make([
        'name'  => 'Cliente',
        'email' => 'cliente@example.com',
        'type'  => TypeUsers::Customer,
    ]);

    $mail = (new NewUserNotification('secret-123'))->toMail($customer);

    expect($mail->actionText)->toBeNull()
        ->and($mail->actionUrl)->toBeNull()
        ->and(implode(' ', $mail->introLines))->not->toContain('secret-123')
        ->and(implode(' ', $mail->introLines))->not->toContain('cliente@example.com');
});
