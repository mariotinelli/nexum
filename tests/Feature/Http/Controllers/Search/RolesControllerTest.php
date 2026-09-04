<?php

declare(strict_types = 1);

use App\Models\Role;

use function Pest\Laravel\getJson;

it('returns paginated roles resource', function (): void {
    Role::factory()->create(['name' => 'Admin']);
    Role::factory()->create(['name' => 'Operator']);

    getJson('/search/roles')
        ->assertSuccessful()
        ->assertJsonStructure(['data', 'links', 'meta']);
});

it('filters roles by search and excludes selected ids', function (): void {
    $admin    = Role::factory()->create(['name' => 'Admin']);
    $operator = Role::factory()->create(['name' => 'Operator']);

    getJson('/search/roles?search=Admin&selected[]=' . $operator->id . '&page=1')
        ->assertSuccessful()
        ->assertJsonFragment(['id' => $admin->id, 'name' => 'Admin'])
        ->assertJsonMissing(['id' => $operator->id, 'name' => 'Operator']);
});

it('returns selected roles merged when selected is sent without page', function (): void {
    $selected = Role::factory()->create(['name' => 'Selected']);

    getJson('/search/roles?selected[]=' . $selected->id)
        ->assertSuccessful()
        ->assertJsonFragment(['id' => $selected->id, 'name' => 'Selected']);
});
