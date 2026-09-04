<?php

declare(strict_types = 1);

namespace App\Models;

use App\Casts\Datetime;
use App\Enums\TypeUsers;
use App\Traits\HandleRole;
use App\Traits\Models\HasTrashedScopes;
use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Database\Eloquent\Attributes\Hidden;
use Illuminate\Database\Eloquent\Attributes\Scope;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Illuminate\Support\Carbon;
use OwenIt\Auditing\Contracts\Auditable;

/**
 * @property int $id
 * @property string $name
 * @property ?int $role_id
 * @property string $email
 * @property ?Carbon $email_verified_at
 * @property string $password
 * @property ?string $remember_token
 * @property ?Carbon $created_at
 * @property ?Carbon $updated_at
 * @property ?Carbon $deleted_at
 * @property string $initials
 * @property string $formatted_name
 * @property TypeUsers $type
 * @property ?Role $role
 */
#[Hidden(['password', 'remember_token'])]
class User extends Authenticatable implements MustVerifyEmail, Auditable
{
    use \OwenIt\Auditing\Auditable;
    use HasFactory;
    use Notifiable;
    use HandleRole;
    use SoftDeletes;
    use HasTrashedScopes;

    protected function casts(): array
    {
        return [
            'email_verified_at' => Datetime::class,
            'type'              => TypeUsers::class,
            'password'          => 'hashed',
        ];
    }

    // Region relationships

    // Endregion

    // Region accessors
    public function getInitialsAttribute(): string
    {
        return str($this->name)->substr(0, 2)->upper()->toString();
    }

    public function getFormattedNameAttribute(): string
    {
        return $this->name;
    }
    // Endregion

    // Region scopes
    #[Scope]
    protected function search(Builder $query, ?string $search): void
    {
        $query->when($search, function (Builder $query) use ($search): void {
            $query->whereAny([
                'users.name',
                'users.email',
            ], 'like', "%{$search}%");
        });
    }
    // Endregion

    // Region methods
    public function isAdmin(): bool
    {
        return $this->type === TypeUsers::Admin;
    }

    public function isCustomer(): bool
    {
        return $this->type === TypeUsers::Customer;
    }

    public function isUser(): bool
    {
        return $this->type === TypeUsers::User;
    }

    public function isSupportRemSoft(): bool
    {
        return $this->type === TypeUsers::SupportRemSoft;
    }
    // Endregion
}
