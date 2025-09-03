import React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useI18n } from "@/i18n/I18nProvider";

export type SignInValues = {
  fullName: string;
  email: string;
};

const SignIn: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useI18n();
  const schema = z.object({
    fullName: z
      .string()
      .min(2, t('val.signin.name.required')),
    email: z
      .string()
      .email(t('val.signin.email.invalid')),
  });
  const form = useForm<SignInValues>({
    resolver: zodResolver(schema),
    defaultValues: { fullName: "", email: "" },
    mode: "onSubmit",
  });

  const onSubmit = (values: SignInValues) => {
    try {
      localStorage.setItem(
        "yg_profile",
        JSON.stringify({ fullName: values.fullName, email: values.email })
      );
    } catch {}
    navigate("/dashboard");
  };

  return (
    <div className="container mx-auto max-w-md px-4 py-10">
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle>{t('signin.title')}</CardTitle>
        </CardHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="fullName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t('signin.fullName.label')}</FormLabel>
                    <FormControl>
                      <Input placeholder={t('signin.fullName.placeholder')} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t('signin.email.label')}</FormLabel>
                    <FormControl>
                      <Input placeholder={t('signin.email.placeholder')} type="email" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button type="submit">{t('signin.submit')}</Button>
            </CardFooter>
          </form>
        </Form>
      </Card>
    </div>
  );
};

export default SignIn;
