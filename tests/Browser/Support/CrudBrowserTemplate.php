<?php

declare(strict_types = 1);

namespace Tests\Browser\Support;

final class CrudBrowserTemplate
{
    /**
     * @param  object  $page
     * @param  array<string, mixed>  $flow
     */
    public static function run(object $page, array $flow): void
    {
        $page->wait(1)->assertSee($flow['indexTitle']);

        self::runCreateFlow($page, $flow['create']);
        self::runUpdateFlow($page, $flow['update']);

        if (isset($flow['delete'])) {
            self::runDeleteFlow($page, $flow['delete']);
        }

        if (isset($flow['restore'])) {
            self::runRestoreFlow($page, $flow['restore']);
        }

        $page->assertNoJavaScriptErrors();
    }

    /**
     * @param  object  $page
     * @param  array<string, mixed>  $create
     */
    private static function runCreateFlow(object $page, array $create): void
    {
        $page->click($create['open'])
            ->assertSee($create['modalTitle'])
            ->type($create['nameField'], $create['name']);

        foreach ($create['extraFields'] ?? [] as $selector => $value) {
            $page->type($selector, (string) $value);
        }

        foreach ($create['clicks'] ?? [] as $selector) {
            $page->click((string) $selector);
        }

        if (isset($create['usageSelect'], $create['usageOption'])) {
            $page->click($create['usageSelect'])
                ->click($create['usageOption'])
                ->click($create['usageSelect']);
        }

        if (isset($create['relationSelect'], $create['relationOption'])) {
            $page->click($create['relationSelect'])
                ->click($create['relationOption'])
                ->click($create['relationSelect']);
        }

        $page->click($create['submit'])
            ->assertSee($create['name'])
            ->assertSee($create['toast'])
            ->assertNoJavaScriptErrors();
    }

    /**
     * @param  object  $page
     * @param  array<string, mixed>  $update
     */
    private static function runUpdateFlow(object $page, array $update): void
    {
        $page->click($update['open'])
            ->assertSee($update['modalTitle'])
            ->assertValue($update['nameField'], $update['oldName'])
            ->clear($update['nameField'])
            ->type($update['nameField'], $update['newName'])
            ->click($update['submit'])
            ->assertSee($update['newName'])
            ->assertSee($update['toast'])
            ->assertNoJavaScriptErrors();
    }

    /**
     * @param  object  $page
     * @param  array<string, string>  $delete
     */
    private static function runDeleteFlow(object $page, array $delete): void
    {
        $page->click($delete['open'])
            ->click($delete['submit'])
            ->assertSee($delete['status'])
            ->assertSee($delete['toast'])
            ->assertNoJavaScriptErrors();
    }

    /**
     * @param  object  $page
     * @param  array<string, string>  $restore
     */
    private static function runRestoreFlow(object $page, array $restore): void
    {
        $page->click($restore['open'])
            ->click($restore['submit'])
            ->assertSee($restore['status'])
            ->assertSee($restore['toast'])
            ->assertNoJavaScriptErrors();
    }
}
