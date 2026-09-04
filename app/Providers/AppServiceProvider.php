<?php

declare(strict_types = 1);

namespace App\Providers;

use App\Enums\Can;
use App\Enums\Queues;
use App\Mail\BrevoTransport;
use App\Models\User;
use Carbon\Carbon;
use Illuminate\Auth\Events\Login as LoginEvent;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\Relation;
use Illuminate\Foundation\DevCommands;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cookie;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Gate;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\URL;
use Illuminate\Support\Facades\Vite;
use Illuminate\Support\ServiceProvider;
use Illuminate\Validation\Rules\Password;

use Opcodes\LogViewer\Facades\LogViewer;
use Spatie\Browsershot\Browsershot;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->configBrowsershot();
    }

    public function boot(): void
    {
        $this->configDatabase();
        $this->configCommands();
        $this->configModels();
        $this->configRules();
        $this->configGates();
        $this->configMorphs();
        $this->configLogViewer();
        $this->configVite();
        $this->configHttp();
        $this->configCarbon();
        $this->configQaEnvBar();
        $this->configBrevo();
        $this->configArtisanDev();
    }

    private function configDatabase(): void
    {
        Schema::defaultStringLength(191);
    }

    private function configCommands(): void
    {
        DB::prohibitDestructiveCommands(app()->isProduction());
    }

    private function configModels(): void
    {
        Model::unguard();

        Model::shouldBeStrict(!app()->isProduction());
    }

    private function configRules(): void
    {
        Password::defaults(function () {
            return Password::min(8)->mixedCase()->numbers()->symbols()->uncompromised();
        });
    }

    private function configGates(): void
    {
        foreach (Can::allCases() as $permission) {
            Gate::define($permission->value, fn (User $user): bool => $user->hasPermissionTo($permission) || $user->isAdmin());
        }
    }

    private function configMorphs(): void
    {
        Relation::morphMap([]);
    }

    private function configLogViewer(): void
    {
        LogViewer::auth(fn (Request $request): bool => $request->user()->isAdmin());
    }

    private function configVite(): void
    {
        Vite::useAggressivePrefetching();
    }

    private function configHttp(): void
    {
        URL::forceHttps(app()->isProduction());
    }

    private function configCarbon(): void
    {
        Carbon::macro('diffInWholeDays', function (mixed $date = null, bool $absolute = true, bool $utc = false): int {
            $date    = Carbon::parse($date);
            $current = $this->copy();

            if ($utc || ($date->timezoneName !== $current->timezoneName)) {
                $date    = $date->utc();
                $current = $current->utc();
            }

            $diff = $current->diffInDays($date, $absolute);

            return (int) round($diff);
        });
    }

    private function configBrowsershot(): void
    {
        if (!app()->isLocal()) {
            $this->app->resolving(Browsershot::class, function (Browsershot $browsershot) {
                $browsershot
                    ->setChromePath('/opt/puppeteer/chrome/linux-141.0.7390.78/chrome-linux64/chrome')
                    ->setNodeBinary('/usr/bin/node');
            });
        }
    }

    private function configQaEnvBar(): void
    {
        Event::listen(LoginEvent::class, function (): void {
            if (!app()->environment('qa')) {
                return;
            }

            Cookie::queue(Cookie::forever('qa_envbar_enabled', '1'));
        });
    }

    private function configBrevo(): void
    {
        Mail::extend('brevo', function (array $config) {
            return new BrevoTransport((string) ($config['api_key'] ?? config('services.brevo.key')));
        });
    }

    private function configArtisanDev(): void
    {
        DevCommands::artisan('schedule:work --whisper', 'schedule')->color('blue');

        if (config('app.sail.enabled')) {
            DevCommands::except('queue', 'server');
            DevCommands::artisan('horizon', 'horizon')->color('red');

            return;
        }

        $queues = collect(Queues::cases())
            ->map(fn (Queues $queue) => $queue->value)
            ->implode(',');

        DevCommands::except('server', 'horizon');
        DevCommands::artisan("queue:listen --tries=1 --timeout=0 --queue=$queues", 'queue')->color('red');
    }
}
