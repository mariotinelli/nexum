<?php

declare(strict_types = 1);

use App\Livewire\Notifications;
use App\Models\User;
use Illuminate\Notifications\DatabaseNotification;

use function Pest\Livewire\livewire;

beforeEach(function (): void {
    $this->user = actingAsUser();
});

it('can render the component', function (): void {
    livewire(Notifications::class)
        ->assertOk()
        ->assertSet('sidepageOpen', false);
});

it('can open and close sidepage', function (): void {
    livewire(Notifications::class)
        ->call('openSidepage')
        ->assertSet('sidepageOpen', true)
        ->call('closeSidepage')
        ->assertSet('sidepageOpen', false);
});

it('can list all notifications for authenticated user', function (): void {
    $otherUser = User::factory()->create();

    foreach (range(1, 3) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $this->user->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
        ]);
    }

    foreach (range(1, 2) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $otherUser->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
        ]);
    }

    livewire(Notifications::class)
        ->assertSet('notifications', function ($notifications): bool {
            expect($notifications)->toHaveCount(3)
                ->and($notifications->every(fn ($notification) => $notification->notifiable_id === user()->id))->toBeTrue();

            return true;
        });
});

it('can list only unread notifications', function (): void {
    foreach (range(1, 3) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $this->user->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
            'read_at'         => null,
        ]);
    }

    foreach (range(1, 2) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $this->user->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
            'read_at'         => now(),
        ]);
    }

    livewire(Notifications::class)
        ->assertSet('unreadNotifications', function ($notifications): bool {
            expect($notifications)->toHaveCount(3)
                ->and($notifications->every(fn ($notification) => $notification->read_at === null))->toBeTrue();

            return true;
        });
});

it('can mark all notifications as read', function (): void {
    foreach (range(1, 5) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $this->user->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
            'read_at'         => null,
        ]);
    }

    expect($this->user->unreadNotifications()->count())->toBe(5);

    livewire(Notifications::class)
        ->call('markAllAsRead')
        ->assertDispatched('notifications::updated');

    expect($this->user->fresh()->unreadNotifications()->count())->toBe(0);
});

it('can delete a specific notification', function (): void {
    $notifications = collect();

    foreach (range(1, 3) as $i) {
        $notifications->push(DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $this->user->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
        ]));
    }

    $notificationToDelete = $notifications->first();

    livewire(Notifications::class)
        ->call('delete', $notificationToDelete->id)
        ->assertDispatched('notifications::updated');

    expect($this->user->fresh()->notifications()->count())->toBe(2)
        ->and(DatabaseNotification::find($notificationToDelete->id))->toBeNull();
});

it('cannot delete notification from another user', function (): void {
    $otherUser = User::factory()->create();

    $notification = DatabaseNotification::create([
        'id'              => fake()->uuid(),
        'type'            => 'App\Notifications\TestNotification',
        'notifiable_type' => User::class,
        'notifiable_id'   => $otherUser->id,
        'data'            => ['title' => 'Test', 'body' => 'Body'],
    ]);

    livewire(Notifications::class)
        ->call('delete', $notification->id)
        ->assertDispatched('notifications::updated');

    expect(DatabaseNotification::find($notification->id))->not->toBeNull();
});

it('can delete all notifications', function (): void {
    foreach (range(1, 5) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $this->user->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
        ]);
    }

    expect($this->user->notifications()->count())->toBe(5);

    livewire(Notifications::class)
        ->call('deleteAll')
        ->assertDispatched('notifications::updated');

    expect($this->user->fresh()->notifications()->count())->toBe(0);
});

it('does not delete notifications from other users when deleting all', function (): void {
    $otherUser = User::factory()->create();

    foreach (range(1, 3) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $this->user->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
        ]);
    }

    foreach (range(1, 2) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $otherUser->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
        ]);
    }

    livewire(Notifications::class)
        ->call('deleteAll');

    expect($this->user->fresh()->notifications()->count())->toBe(0)
        ->and($otherUser->fresh()->notifications()->count())->toBe(2);
});

it('dispatches notifications::updated event when marking all as read', function (): void {
    foreach (range(1, 3) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $this->user->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
            'read_at'         => null,
        ]);
    }

    livewire(Notifications::class)
        ->call('markAllAsRead')
        ->assertDispatched('notifications::updated');
});

it('dispatches notifications::updated event when deleting all', function (): void {
    foreach (range(1, 3) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $this->user->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
        ]);
    }

    livewire(Notifications::class)
        ->call('deleteAll')
        ->assertDispatched('notifications::updated');
});

it('dispatches notifications::updated event when deleting a specific notification', function (): void {
    $notification = DatabaseNotification::create([
        'id'              => fake()->uuid(),
        'type'            => 'App\Notifications\TestNotification',
        'notifiable_type' => User::class,
        'notifiable_id'   => $this->user->id,
        'data'            => ['title' => 'Test', 'body' => 'Body'],
    ]);

    livewire(Notifications::class)
        ->call('delete', $notification->id)
        ->assertDispatched('notifications::updated');
});

it('orders notifications by latest first', function (): void {
    $oldNotification = DatabaseNotification::create([
        'id'              => fake()->uuid(),
        'type'            => 'App\Notifications\TestNotification',
        'notifiable_type' => User::class,
        'notifiable_id'   => $this->user->id,
        'data'            => ['title' => 'Test', 'body' => 'Body'],
        'created_at'      => now()->subDays(2),
    ]);

    $recentNotification = DatabaseNotification::create([
        'id'              => fake()->uuid(),
        'type'            => 'App\Notifications\TestNotification',
        'notifiable_type' => User::class,
        'notifiable_id'   => $this->user->id,
        'data'            => ['title' => 'Test', 'body' => 'Body'],
        'created_at'      => now(),
    ]);

    $midNotification = DatabaseNotification::create([
        'id'              => fake()->uuid(),
        'type'            => 'App\Notifications\TestNotification',
        'notifiable_type' => User::class,
        'notifiable_id'   => $this->user->id,
        'data'            => ['title' => 'Test', 'body' => 'Body'],
        'created_at'      => now()->subDay(),
    ]);

    livewire(Notifications::class)
        ->assertSet('notifications', function ($notifications) use ($recentNotification, $midNotification, $oldNotification): bool {
            $ids = $notifications->pluck('id')->toArray();

            expect($ids)->toBe([
                $recentNotification->id,
                $midNotification->id,
                $oldNotification->id,
            ]);

            return true;
        });
});

it('handles empty notifications list', function (): void {
    livewire(Notifications::class)
        ->assertSet('notifications', function ($notifications): bool {
            expect($notifications)->toBeEmpty();

            return true;
        })
        ->assertSet('unreadNotifications', function ($notifications): bool {
            expect($notifications)->toBeEmpty();

            return true;
        });
});

it('responds to notifications::updated event', function (): void {
    foreach (range(1, 2) as $i) {
        DatabaseNotification::create([
            'id'              => fake()->uuid(),
            'type'            => 'App\Notifications\TestNotification',
            'notifiable_type' => User::class,
            'notifiable_id'   => $this->user->id,
            'data'            => ['title' => 'Test', 'body' => 'Body'],
        ]);
    }

    livewire(Notifications::class)
        ->assertSet('notifications', function ($notifications): bool {
            expect($notifications)->toHaveCount(2);

            return true;
        })
        ->dispatch('notifications::updated')
        ->assertOk();
});
