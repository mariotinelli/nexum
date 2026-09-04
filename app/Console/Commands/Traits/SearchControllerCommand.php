<?php

declare(strict_types = 1);

namespace App\Console\Commands\Traits;

trait SearchControllerCommand
{
    protected function makeSearchController(): void
    {
        $path = $this->getSearchControllerPath();

        $this->makeDirectory($this->getSearchControllerDirectory($path));

        $contents = $this->getSearchControllerSourceFile();

        if (!$this->filesystem->exists($path)) {
            $this->filesystem->put($path, $contents);
            $this->info("File : {$path} created");
        } else {
            $this->error("File : {$path} already exits");
        }
    }

    protected function getSearchControllerStub(): string
    {
        return __DIR__ . '/../../../../stubs/search-controller.stub';
    }

    protected function getSearchControllerPath(): string
    {
        return app_path('Http/Controllers/Search/' . $this->getPluralModel($this->model)->ucfirst()->toString() . 'Controller.php');
    }

    protected function getSearchControllerSourceFile()
    {
        return $this->getStubContents($this->getSearchControllerStub(), $this->getSearchControllerStubVariables());
    }

    protected function getSearchControllerDirectory(string $path): string
    {
        $lastForwardSlash  = strrpos($path, '/');
        $lastBackwardSlash = strrpos($path, '\\');
        $lastSeparator     = max($lastForwardSlash === false ? -1 : $lastForwardSlash, $lastBackwardSlash === false ? -1 : $lastBackwardSlash);

        return $lastSeparator === -1 ? '.' : substr($path, 0, $lastSeparator);
    }

    protected function getSearchControllerStubVariables(): array
    {
        return [
            'model'           => $this->model,
            'variable'        => $this->getPluralModel($this->model)->snake()->lower()->toString(),
            'pluralModel'     => $this->getPluralModel($this->model)->ucfirst()->toString(),
            'searchAttribute' => $this->searchAttribute,
        ];
    }
}
